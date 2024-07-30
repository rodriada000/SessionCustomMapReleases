#
# Imported module functions
#

# Use our SimpleRequests module for this experimental version.
from SimpleRequests import SimpleRequest
from SimpleRequests.SimpleRequest import error

from CatalogBuilder.PostedMessage import PostedMessage
from CatalogBuilder.CatalogItem import CatalogItem
from CatalogBuilder.Catalog import Catalog


# Use the datetime module for generating timestamps and snowflakes.
from datetime import datetime, timedelta

# Use the os module for creating directories and writing files.
from os import makedirs, getcwd, path

# Use the random module to choose from a list at random.
from random import choice

# Convert JSON to a Python dictionary for ease of traversal.
from json import loads,dump

from random import randint
from time import sleep

#
# Lambda functions
#

# Return a random string of a specified length.
random_str = lambda length: ''.join([choice('0123456789ABCDEF') for i in range(length)])


# Return a Discord snowflake from a timestamp.
snowflake = lambda timestamp_s: (timestamp_s * 1000 - 1420070400000) << 22

# Return a timestamp from a Discord snowflake.
timestamp = lambda snowflake_t: ((snowflake_t >> 22) + 1420070400000) / 1000.0


#
# Classes
#


class DiscordConfig(object):
    """Just a class used to store configs as objects."""


class Discord:
    """Experimental Discord scraper class."""

    def __init__(self, config='config.json', apiver='v6'):
        """Discord constructor.

        :param config: The configuration JSON file.
        :param apiver: The current Discord API version.
        """

        with open(config, 'r') as configfile:
            configdata = loads(configfile.read())

        cfg = type('DiscordConfig', (object,), configdata)()
        if cfg.token == "" or cfg.token is None:
            error('You must have an authorization token set in %s' % config)
            exit(-1)

        self.api = apiver
        self.buffer = cfg.buffer

        self.headers = {
            'user-agent': cfg.agent,
            'authorization': cfg.token
        }

        self.types = cfg.types
        self.query = self.create_query_body(
            images=cfg.query['images'],
            files=cfg.query['files'],
            embeds=cfg.query['embeds'],
            links=cfg.query['links'],
            videos=cfg.query['videos'],
            nsfw=cfg.query['nsfw']
        )

        self.directs = cfg.directs if len(cfg.directs) > 0 else {}
        self.servers = cfg.servers if len(cfg.servers) > 0 else {}

        # Save us the time by exiting out when there's nothing to scrape.
        if len(cfg.directs) == 0 and len(cfg.servers) == 0:
            error('No servers or DMs were set to be grabbed, exiting.')
            exit(0)

    def get_day(self, day, month, year):
        """Get the timestamps from 00:00 to 23:59 of the given day.

        :param day: The target day.
        :param month: The target month.
        :param year: The target year.
        """

        min_time = datetime(year, month, day, 
            hour=0, minute=0, second=0).timestamp()

        max_time = datetime(year, month, day, 
            hour=23, minute=59, second=59).timestamp()

        return {
            '00:00': snowflake(int(min_time)),
            '23:59': snowflake(int(max_time))
        }

    def safe_name(self, name):
        """Convert name to a *nix/Windows compliant name.

        :param name: The filename to convert.
        """

        output = ""
        for char in name:
            if char not in '\\/<>:"|?*':
                output += char

        return output


    def create_query_body(self, **kwargs):
        """Generate a search query string for Discord."""

        query = ""

        for key, value in kwargs.items():
            if value is True and key != 'nsfw':
                query += '&has=%s' % key[:-1]

            if key == 'nsfw':
                query += '&include_nsfw=%s' % str(value).lower()

        return query


    def get_server_name(self, serverid, isdm=False):
        """Get the server name by its ID.

        :param serverid: The server ID.
        :param isdm: A flag to check whether we're in a DM or not.
        """

        if isdm:
            return serverid

        request = SimpleRequest(self.headers).request
        server = request.grab_page('https://discordapp.com/api/%s/guilds/%s' % (self.api, serverid))

        if server is not None and len(server) > 0:
            return '%s_%s' % (serverid, self.safe_name(server['name']))

        else:
            error('Unable to fetch server name from id, generating one instead.')
            return '%s_%s' % (serverid, random_str(12))

    def get_channel_name(self, channelid, isdm=False):
        """Get the channel name by its ID.

        :param channelid: The channel ID.
        :param isdm: A flag to check whether we're in a DM or not.
        """

        if isdm:
            return channelid

        request = SimpleRequest(self.headers).request
        channel = request.grab_page('https://discordapp.com/api/%s/channels/%s' % (self.api, channelid))

        if channel is not None and len(channel) > 0:
            return '%s_%s' % (channelid, self.safe_name(channel['name']))

        else:
            error('Unable to fetch channel name from id, generating one instead.')
            return '%s_%s' % (channelid, random_str(12))

    @staticmethod
    def get_path_to_scrapes(server=None, channel=None):
        """return path to folder or file of scraped json (creates folder if missing)

        :param server: The server name.
        :param channel: The channel name.
        """

        folder = path.join(getcwd(), 'Discord Scrapes')

        if not path.exists(folder):
            makedirs(folder)

        if server is not None and channel is not None:
            # return path to file if server/channel given
            return path.join(folder, "{}_{}.json".format(server,channel))


        return folder


    def grab_channel_data(self, server, channel, start_date=None, isdm=False):
        """Returns dict of all messages pulled from server/channel up to a given day.
        pulls for the past day if no cutoff date given 

        :param server: The server name.
        :param channel: The channel name.
        :param start_date: the date to start pulling
        :param isdm: A flag to check whether we're in a DM or not.
        """

        today = datetime.today().date()
        today += timedelta(days=-179)

        if start_date is None:
            start_date = (today + timedelta(days=-1))

        results = []

        while start_date.date() <= today: 
            request = SimpleRequest(self.headers).request
            loop_date = self.get_day(start_date.day, start_date.month, start_date.year)

            print('   pull for {}'.format(start_date.isoformat()))

            if not isdm:
                request.set_header('referer', 'https://discordapp.com/channels/%s/%s' % (server, channel))
                content = request.grab_page(
                    'https://discordapp.com/api/%s/guilds/%s/messages/search?channel_id=%s&min_id=%s&max_id=%s&%s' %
                    (self.api, server, channel, loop_date['00:00'], loop_date['23:59'], self.query)
                )
            else:
                request.set_header('referer', 'https://discordapp.com/channels/@me/%s' % channel)
                content = request.grab_page(
                    'https://discordapp.com/api/%s/channels/%s/messages/search?min_id=%s&max_id=%s&%s' %
                    (self.api, channel, loop_date['00:00'], loop_date['23:59'], self.query)
                )

            if content is None:
                # failed http request so break out and stop scraping
                break

            try:
                if content['messages'] is not None:
                    for messages in content['messages']:
                        for message in messages:
                            results.append({
                                 'id': message['id']
                                ,'authorName': '%s#%s' % (message['author']['username'], message['author']['discriminator'])
                                ,'content': message['content']
                                ,'timestamp': message['timestamp']
                                ,'attachments': message['attachments']
                                ,'embed': message['embeds']
                            })

            except TypeError:
                continue
            
            start_date += timedelta(days=1)
            sleep(randint(5,8))
        
        return results

    def merge_and_save(self, message_data, server, channel):
        """
            Saved scraped discord data to a .json file.
            if file exists already then checks if message already saved before adding.
        """
        saved_data = {}
        saved_ids = []
        filepath = self.get_path_to_scrapes(server,channel)

        if path.exists(filepath):
            with open (filepath, 'r') as channel_file:
                saved_data = loads(channel_file.read())
            saved_ids = [x.get('id') for x in saved_data['data']]
        else:
            saved_data = {
                'server': server,
                'channel': channel,
                'scrapeDate': datetime.today().isoformat(),
                'data': []
            }

        for m in message_data:
            if m.get('id') not in saved_ids:
                saved_data['data'].append(m)
        
        saved_data['scrapeDate'] = datetime.today().isoformat()
        # saved_data['data'] = self.refresh_urls(saved_data['data'], server, channel)
        saved_data['data'] = sorted(saved_data['data'], key=lambda x: datetime.fromisoformat(x['timestamp']))

        with open(filepath, 'w') as fp:
            dump(saved_data, fp, indent=2)

    def refresh_urls(self, messages, server, channel):
        """
        Loops through messages and does an API call if cdn url is expired.
        returns messages
        """
        refreshed_msgs = []
        for m in messages:
            msg = PostedMessage([m])
            url = msg.get_image_url()
            if url is None or 'ex=' not in url:
                refreshed_msgs.append(m)
                continue

            idx = url.index('ex=') + len('ex=')
            url = url[idx:]
            idx = url.index('&')
            hex = url[:idx]
            ex_date = datetime.utcfromtimestamp(int(hex, 16))

            if ex_date >= datetime.today():
                refreshed_msgs.append(m)
                continue

            request = SimpleRequest(self.headers).request
            request.set_header('referer', 'https://discord.com/channels/%s/%s' % (server, channel))
            req_url = 'https://discord.com/api/v9/channels/%s/messages?limit=5&around=%s' % (channel, m['id']) 
            content = request.grab_page(req_url)

            try:
                if content is not None and len(content) > 0:
                    for new_m in content:
                        if new_m['id'] == m['id']:
                            refreshed_msgs.append({
                                'id': new_m['id']
                                ,'authorName': '%s#%s' % (new_m['author']['username'], new_m['author']['discriminator'])
                                ,'content': new_m['content']
                                ,'timestamp': new_m['timestamp']
                                ,'attachments': new_m['attachments']
                                ,'embed': new_m['embeds']
                            })
                            print('... refreshed %s' % m['id'])
                            sleep(randint(4,6))
                            break
            except TypeError:
                refreshed_msgs.append(m)
                continue

        return refreshed_msgs



    def get_last_scrape_date(self, server, channel):
        filepath = self.get_path_to_scrapes(server,channel)

        if path.exists(filepath):
            with open (filepath, 'r') as channel_file:
                saved_data = loads(channel_file.read())
            return datetime.fromisoformat(saved_data['scrapeDate'])
        
        cutoff = datetime.today()
        cutoff += timedelta(days=-180)
        return cutoff

    def grab_server_data(self):
        """Scan and grab the attachments within a server."""

        for server, channels in self.servers.items():
            for channel in channels:
                cutoff = self.get_last_scrape_date(server, channel)
                print('grabbing data for {} : {} back to {} ...'.format(server, channel, cutoff.isoformat()))
                message_data = self.grab_channel_data(server, channel, cutoff)
                self.merge_and_save(message_data, server, channel)
        

    def grab_dm_data(self):
        """Scan and grab the attachments within a direct message."""

        for alias, channel in self.directs.items():
            print('grabbing DM data for {} : {} ...'.format(alias, channel))
            message_data = self.grab_channel_data(alias, channel)
            self.merge_and_save(message_data, alias, channel)
        

#
# Initializer
#

CHANNELS = {
    "943801307280584724" : "session-maps",
    "943801688513454080" : "session-decks",
    "943801383491092481" : "session-shirts",
    "943801432174370886" : "session-pants",
    "943801467133919262" : "session-shoes",
    "943801712551014400" : "session-griptapes",
    "943801342474981396" : "session-hats",
    "943801531998818334" : "session-characters",
    "943801765390864384" : "session-trucks",
    "943801783317299253" : "session-wheels",
    "943801917908348928" : "session-meshes",
    "945412387228495922" : "session-characters",
    "943801815588278292" : "session-characters",
}

if __name__ == '__main__':
    ds = Discord()
    ds.grab_server_data()
    
    catalog = Catalog("Scraped Discord Catalog")

    for server,channels in ds.servers.items():
        for channel in channels:

            with open(ds.get_path_to_scrapes(server, channel), "r") as channelData:
                channelJson = loads(channelData.read())
                messages = channelJson['data']

            for i, m in enumerate(messages):

                if m.get('isProcessed') is True:
                    continue
                
                # if first message doesnt have a link and image check next messages to see if they are related 
                batch = [m]
                msg = PostedMessage(batch)
                j = i+1

                while not msg.has_image_and_download() and j < len(messages) and m['authorName'] == messages[j]['authorName']:
                    if not messages[j].get('isProcessed', False):
                        batch.append(messages[j])

                    msg = PostedMessage(batch)
                    j += 1


                if msg.has_image_and_download():
                    for processed in batch:
                        processed['isProcessed'] = True

                    cat_item = CatalogItem(msg, CHANNELS[channel])

                    if cat_item.is_valid():
                        catalog.add_item(cat_item) 


    with open('ScrapedCatalog.json', 'w') as fc:
        dump(catalog.json(), fc, indent=2)

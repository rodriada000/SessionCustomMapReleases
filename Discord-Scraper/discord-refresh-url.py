#
# Imported module functions
#
from json import loads,dump

from SimpleRequests import SimpleRequest
from SimpleRequests.SimpleRequest import error
from discord import Discord

from CatalogBuilder.PostedMessage import PostedMessage
from CatalogBuilder.CatalogItem import CatalogItem
from CatalogBuilder.Catalog import Catalog

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
    ds.refresh_data_urls()
    
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

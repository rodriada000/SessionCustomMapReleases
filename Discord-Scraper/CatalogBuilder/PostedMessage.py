class PostedMessage():
    """
    Class to treat batch of messages as one message...
    A sequence of messages all relate to each other so this merges all messages into one object
    """
    def __init__(self, messages):
        self.messages = messages
        self.content = ""
        self.attachments = []
        self.embeds = []

        for m in self.messages:
            self.author = m['authorName']
            self.timestamp = m['timestamp']
            self.content = self.content + m['content']
            self.attachments.extend(m['attachments'])
            self.embeds.extend(m['embed'])

    def is_batch(self):
        return len(self.messages) > 1

    def has_attachments(self):
        return len(self.attachments) > 0

    def has_embeds(self):
        return len(self.embeds) > 0

    def get_image_url(self):
        for a in self.attachments:
            if a.get('content_type', '')[0:5] == 'image':
                return a['url']

            if a['filename'][-4:] in [".png", "jpeg", ".jpg"]:
                return a['url']

        for e in self.embeds:
            if e.get('type','') == 'image':
                return e.get('url', None)


        return None

    def get_download(self, part='url'):
        for a in self.attachments:
            if a.get('content_type') in ["application/zip", "application/rar"]:
                return a[part]
            
            if a['filename'][-3:] in ["rar", "zip"]:
                return a[part]

        if part == 'filename': 
            part = 'title' # embeds json goes by 'title'

        for e in self.embeds:
            if e['type'] == 'link':
                if e.get('provider') is not None and e['provider']['name'] in ['Google Docs']:
                    return e[part]
                if ".zip" in e.get('title', '') or ".rar" in e.get('title', ''):
                    return e[part]
                if 'mega.nz' in e.get('url',''): 
                    return e[part]

        return None

    def has_image_and_download(self):
        return self.get_image_url() is not None and self.get_download('url') is not None

    def __str__(self):
        return str({'author': self.author, 'content': self.content, 'is_batch': self.is_batch(), 'attachmentCount': len(self.attachments), 'embedCount': len(self.embeds)})


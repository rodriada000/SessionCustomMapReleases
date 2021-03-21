
class CatalogItem():

    def __init__(self, message, category):
        self.ID = message.get_download('filename')
        self.Name = message.get_download('filename')[:-4]
        self.Description = message.content
        self.Version = 1
        self.Author = message.author
        self.DownloadLink = self.convert_url(message.get_download('url'))
        self.PreviewImage = message.get_image_url()
        self.Category = category
        self.UpdatedDate = message.timestamp

    def convert_url(self, url):
        if "google" in url:
            gUrl = url.replace("https://drive.google.com/file/d/", "")
            return "rsmm://GDrive/" + gUrl[:gUrl.find("/")]
        elif "mega.nz" in url:
            megaUrl = url.replace("https://mega.nz/file/", "")
            return "rsmm://MegaFile/" + megaUrl

        return "rsmm://Url/" + url.replace("://", "$")
    
    def __str__(self):
        return str(self.json())

    def json(self):
        return {
            "ID": self.ID,
            "Name": self.Name,
            "Description": self.Description,
            "Version": self.Version,
            "Author": self.Author,
            "DownloadLink": self.DownloadLink,
            "PreviewImage": self.PreviewImage,
            "Category": self.Category,
            "UpdatedDate": self.UpdatedDate           
        }



class CatalogItem():

    def __init__(self, message, category):
        self.ID = message.get_download('filename')
        self.Name = message.get_download('filename')[:-4]
        self.Description = message.content

        if message.get_download('url') is not None:
            self.Description = self.Description.replace(message.get_download('url'), '')

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
            idx = url.find("https://mega.nz/file/") + len("https://mega.nz/file/")
            return "rsmm://MegaFile/" + url[idx:]

        return "rsmm://Url/" + url.replace("://", "$")

    def is_valid(self):
        if len(self.DownloadLink) <= len("rsmm://MegaFile/gy5WmAzA"):
            return False

        if self.ID[-4:] not in [".zip", ".rar"]:
            return False

        return True
    
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


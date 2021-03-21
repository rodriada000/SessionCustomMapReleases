
class Catalog():

    def __init__(self, name):
        self.Name = name
        self.Assets = []

    def add_item(self, item):
        if item.DownloadLink not in [i.DownloadLink for i in self.Assets]:
            self.Assets.append(item)

    def __str__(self):
        return str(self.json())
    
    def json(self):
        return {"Name": self.Name, "Assets": [a.json() for a in self.Assets]}
class Article:
    def __init__ (self, _name:str, _authorName:str, _authorLink:str, _URL:str, _creationDate:int, _telegraphLinks:list, _tags:list=None):
        self.name = _name
        self.authorName = _authorName
        self.authorLink = _authorLink
        self.URL = _URL
        self.creationDate = _creationDate
        self.telegraphLinks = _telegraphLinks
        self.tags = _tags
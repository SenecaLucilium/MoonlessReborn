class Article:
    def __init__ (self, _name:str, _authorName:str, _authorLink:str, _URL:str, _creationDate:int, _telegraphLinks:list, _tags:list=None):
        self.name = _name
        self.authorName = _authorName
        self.authorLink = _authorLink
        self.URL = _URL
        self.creationDate = _creationDate
        self.telegraphLinks = _telegraphLinks
        self.tags = _tags
    
    def __eq__(self, other):
        if isinstance(other, Article):
            return (self.name == other.name and
                    self.authorName == other.authorName and
                    self.URL == other.URL and
                    self.creationDate == other.creationDate)
        return False

    def __hash__ (self):
        return hash((self.name, self.authorName, self.URL, self.creationDate))
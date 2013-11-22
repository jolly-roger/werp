from datetime import datetime

from werp.orm.base import *

class Article(DBase):
    __tablename__ = 'ukrainianside_article'
    id = Column(BigInteger, primary_key = True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    content = Column(String)
    order = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    
    def __init__(self, name=None, description=None, content=None, order=None, url=None):
        self.name = name
        self.description = description
        self.content = content
        self.order = order
        self.url = url
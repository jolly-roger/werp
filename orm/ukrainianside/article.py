from datetime import datetime

from werp.orm.base import *

class Article(DBase):
    __tablename__ = 'ukrainianside_article'
    id = Column(BigInteger, primary_key = True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    content = Column(String)
    order = Column(Integer, nullable=False)
    alias = Column(String, nullable=False)
    
    def __init__(self, name=None, description=None, content=None, order=None):
        self.title = title
        self.description = description
        self.content = content
        self.order = order
        self.url = url
        self.alias = alias
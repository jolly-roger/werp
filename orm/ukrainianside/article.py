from datetime import datetime

from werp.orm.base import *

class Article(DBase):
    __tablename__ = 'ukrainianside_article'
    id = Column(BigInteger, primary_key = True)
    title = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    alias = Column(String, nullable=False)
    
    def __init__(self, name=None, order=None):
        self.title = title
        self.order = order
        self.alias = alias
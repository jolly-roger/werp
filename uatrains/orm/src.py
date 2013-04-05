from .base import *


class Src(DBase):
    __tablename__ = 'src'
    id = Column(BigInteger, primary_key = True)
    alias = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type = Column(BigInteger, nullable=False)
    ua_url = Column(String)
    ru_url = Column(String)
    en_url = Column(String)

    def __init__(self, alias=None, url=None, type=None, ua_url=None, ru_url=None, en_url=None):
        self.alias = alias
        self.url = url
        self.type = type
        self.ua_url = ua_url
        self.ru_url = ru_url
        self.en_url = en_url
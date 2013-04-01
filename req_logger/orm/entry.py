from .base import *


class Entry(DBase):
    __tablename__ = 'entry'
    id = Column(BigInteger, primary_key = True)
    value = Column(Text)
    is_parsed = Column(Boolean)
    
    def __init__(self, value=None, is_parsed=False):
        self.value = value
        self.is_parsed = is_parsed
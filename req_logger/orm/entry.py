from .base import *


class Entry(DBase):
    __tablename__ = 'entry'
    id = Column(BigInteger, primary_key = True)
    value = Column(Text)
    
    def __init__(self, value=None):
        self.value = value
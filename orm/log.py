from .base import *


class Log(DBase):
    __tablename__ = 'log'
    id = Column(postgresql.UUID, primary_key = True)
    value = Column(Text)
    is_parsed = Column(Boolean)
    
    def __init__(self, value=None, is_parsed=False):
        self.value = value
        self.is_parsed = is_parsed
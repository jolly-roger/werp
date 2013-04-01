from .base import *


class UserAgent(DBase):
    __tablename__ = 'user_agent'
    id = Column(BigInteger, primary_key = True)
    value = Column(Text)
    
    def __init__(self, value=None):
        self.value = value
from .base import *


class UserAgent(DBase):
    __tablename__ = 'user_agent'
    id = Column(BigInteger, primary_key = True)
    value = Column(Text)
    is_bot = Column(Boolean)
    
    def __init__(self, value=None, is_bot=False):
        self.value = value
        self.is_bot = is_bot
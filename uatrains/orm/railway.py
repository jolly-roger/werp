from .base import *


class Railway(DBase):
    __tablename__ = 'railway'
    id = Column(BigInteger, primary_key = True)
    title = Column(String)

    def __init__(self, title=None):
        self.title = title
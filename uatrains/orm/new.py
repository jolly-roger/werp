from .base import *


class New(DBase):
    __tablename__ = 'uatrains_new'
    id = Column(BigInteger, primary_key = True)
    value = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    lng = Column(String, nullable=False)

    def __init__(self, value=None, date=None, lng=None):
        self.value = value
        self.date = date
        self.lng = lng
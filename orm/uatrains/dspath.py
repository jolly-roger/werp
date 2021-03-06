from werp.orm.base import *


class Dspath(DBase):
    __tablename__ = 'uatrains_dspath'
    id = Column(BigInteger, primary_key = True)
    src_id = Column(BigInteger, ForeignKey('uatrains_src.id'), nullable=False)
    value = Column(String, nullable=False)
    dstype = Column(BigInteger, nullable=False)
    
    data_src = relationship('Src', backref='dspathes')

    def __init__(self, src_id=None, value=None, dstype=None):
        self.src_id = src_id
        self.value = value
        self.dstype = dstype
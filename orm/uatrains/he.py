from datetime import datetime

from werp.orm.base import *


class He(DBase):
    __tablename__ = 'uatrains_he'
    id = Column(BigInteger, primary_key = True)
    eid = Column(BigInteger, nullable=False)
    oid = Column(BigInteger)
    etype = Column(SmallInteger, nullable=False)
    value = Column(String)
    ua_title = Column(String)
    ua_period = Column(String)
    vc = Column(BigInteger, nullable=False, default=0)
    ref_id = Column(BigInteger)
    c_date = Column(DateTime, nullable=False, default=datetime.now)
    hc_date = Column(DateTime, nullable=False, default=datetime.now)
    htype = Column(SmallInteger, nullable=False)

    def __init__(self, eid=None, oid=None, etype=None, value=None, ua_title=None, ua_period=None, vc=None, ref_id=None,
        c_date=None, hc_date=None, htype=None):
        self.eid = eid
        self.oid = oid
        self.etype = etype
        self.value = value
        self.ua_title = ua_title
        self.ua_period = ua_period
        self.vc = vc
        self.ref_id = ref_id
        self.c_date = c_date
        self.hc_date = hc_date
        self.htype = htype
        
def from_e(e, htype):
    return He(e.id, e.oid, e.etype, e.value, e.ua_title, e.ua_period, e.vc, e.ref_id, e.c_date, datetime.now(), htype)
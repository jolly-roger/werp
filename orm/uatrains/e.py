from werp.orm.base import *


class E(DBase):
    __tablename__ = 'uatrains_e'
    id = Column(BigInteger, primary_key = True)
    etype = Column(SmallInteger, nullable=False)
    value = Column(String)
    oid = Column(BigInteger)
    ua_title = Column(String)
    ru_title = Column(String)
    en_title = Column(String)
    ua_period = Column(String)
    ru_period = Column(String)
    en_period = Column(String)
    vc = Column(BigInteger, nullable=False, default=0)
    
    t_ss = relationship('TrainStation', primaryjoin='E.id==TrainStation.t_id', foreign_keys='TrainStation.t_id',
        order_by='TrainStation.order', backref='t')
    s_ts = relationship('TrainStation', primaryjoin='E.id==TrainStation.s_id', foreign_keys='TrainStation.s_id',
        order_by='[TrainStation.departure, TrainStation.arrival]', backref='s')
    
    def __init__(self, etype=None, value=None, oid=None, ua_title=None, ru_title=None, en_title=None,
        ua_period=None, ru_period=None, en_period=None):
        self.etype = etype
        self.value = value
        self.oid = oid
        self.ua_title = ua_title
        self.ru_title = ru_title
        self.en_title = en_title
        self.ua_period = ua_period
        self.ru_period = ru_period
        self.en_period = en_period
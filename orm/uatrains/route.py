from werp.orm.base import *


class Route(DBase):
    __tablename__ = 'uatrains_route'
    id = Column(BigInteger, primary_key = True)
    rid = Column(BigInteger, unique=True)
    title = Column(String)
    value = Column(String)
    reverse_title = Column(String)
    reverse_value = Column(String)
    railway_id = Column(BigInteger, ForeignKey('uatrains_railway.id'))
    
    route_trains = relationship('RouteTrain', backref='route')
    railway = relationship('Railway', backref='routes')

    def __init__(self, rid=None, title=None, value=None, reverse_title=None, reverse_value=None, railway_id=None):
        self.rid = rid
        self.title = title
        self.value = value
        self.reverse_title = reverse_title
        self.reverse_value = reverse_value
        self.railway_id = railway_id
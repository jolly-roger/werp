from werp.orm.base import *


class TrainStation(DBase):
	__tablename__ = 'uatrains_train_station'
	id = Column(BigInteger, primary_key = True)
	t_id = Column(BigInteger, ForeignKey('uatrains_e.id'), nullable=False)
	s_id = Column(BigInteger, ForeignKey('uatrains_e.id'), nullable=False)
	arrival = Column(String)
	departure = Column(String)
	halt = Column(String)
	order = Column(Integer)
	date_from = Column(Date)
	date_to = Column(Date)
	
	t = relationship('E', primaryjoin='and_(TrainStation.t_id == E.id, E.ref_id is None)')
	s = relationship('E', primaryjoin='TrainStation.s_id == E.id')
	
	def __init__(self, t_id, s_id, order, arrival=None, departure=None, halt=None, date_from=None,
		date_to=None):
		self.t_id = t_id
		self.s_id = s_id
		self.order = order
		self.arrival = arrival
		self.departure = departure
		self.halt = halt
		self.date_from = date_from
		self.date_to = date_to
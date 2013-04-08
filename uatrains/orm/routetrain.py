from .base import *


class RouteTrain(DBase):
	__tablename__ = 'uatrains_route_train'
	id = Column(BigInteger, primary_key = True)
	route_id = Column(BigInteger, ForeignKey('route.id'), nullable=False)
	t_id = Column(BigInteger, ForeignKey('e.id'), nullable=False)
	is_reverse = Column(Boolean, nullable=False, default=False)
	
	train = relationship('E', backref='train_routes')
	
	def __init__(self, route_id, t_id, is_reverse=False):
		self.route_id = route_id
		self.t_id = t_id
		self.is_reverse = is_reverse
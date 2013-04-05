import logging

from .. import orm


logger = logging.getLogger('werp_error.uatrains_spider')


def is_added(train_station, ses):
	ret = False
	try:
		ses.query(orm.TrainStation).filter(orm.and_(orm.and_(orm.TrainStation.t_id == train_station.t_id,
			orm.TrainStation.s_id == train_station.s_id),
			orm.TrainStation.order == train_station.order)).one()
		ret = True
	except:
		pass
	return ret
def is_changed(train_station, ses):
	ret = False
	try:
		ts = ses.query(orm.TrainStation).filter(orm.and_(orm.and_(orm.TrainStation.t_id == train_station.t_id,
			orm.TrainStation.s_id == train_station.s_id),
			orm.TrainStation.order == train_station.order)).one()
		if ts.arrival != train_station.arrival or ts.departure != train_station.departure or \
			ts.halt != train_station.halt or ts.order != train_station.order or \
			ts.date_from != train_station.date_from or ts.date_to != train_station.date_to:
			ret = True
	except:
		ret = True
	return ret
def load_changes(train_station, ses):
	ts = ses.query(orm.TrainStation).filter(orm.and_(orm.and_(orm.TrainStation.t_id == train_station.t_id,
		orm.TrainStation.s_id == train_station.s_id),
		orm.TrainStation.order == train_station.order)).one()
	ts.arrival = train_station.arrival
	ts.departure = train_station.departure
	ts.halt = train_station.halt
	ts.order = train_station.order
	ts.date_from = train_station.date_from
	ts.date_to = train_station.date_to
	return ts
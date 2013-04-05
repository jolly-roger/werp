#from .. import orm
#
#
#def is_added(route_train, ses):
#	ret = False
#	try:
#		ses.query(orm.RouteTrain).filter(orm.and_(orm.RouteTrain.route_id == route_train.route_id,
#			orm.RouteTrain.t_id == route_train.t_id)).one()
#		ret = True
#	except orm.NoResultFound:
#		pass
#	return ret
#def is_changed(route_train, ses):
#	ret = False
#	try:
#		rt = ses.query(orm.RouteTrain).filter(orm.and_(orm.RouteTrain.route_id == route_train.route_id,
#			orm.RouteTrain.t_id == route_train.t_id)).one()
#		if rt.is_reverse != route_train.is_reverse:
#			ret = True
#	except Exception:
#		ret = True
#	return ret
#def load_changes(route_train, ses):
#	rt = ses.query(orm.RouteTrain).filter(orm.and_(orm.RouteTrain.route_id == route_train.route_id,
#		orm.RouteTrain.t_id == route_train.t_id)).one()
#	rt.is_reverse = route_train.is_reverse
#	return rt
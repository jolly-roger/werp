import redis
import traceback
import re

from werp import orm

def is_not_empty(e):
	ret = False
	if e.ua_title is not None and e.value is not None and e.oid is not None:
		ret = True
	return ret
def e_has_all_data(e):
	ret = False
	if e.ua_title is not None and \
		e.value is not None and \
		e.oid is not None:
		ret = True
	return ret
def ts_has_all_data(ts):
	ret = False
	if ts.t_id is not None and \
		ts.s_id is not None and \
		ts.arrival is not None and \
		ts.departure is not None:
		ret = True
	return ret
def get_t(e, ses):
	t = None
	try:
		prepared_ua_title = e.ua_title if e.ua_title is not None else ''
		t = ses.query(orm.uatrains.E).\
			filter(orm.and_(orm.uatrains.E.etype == e.etype, orm.uatrains.E.oid == e.oid,
				orm.uatrains.E.value == e.value, orm.uatrains.E.ua_title == prepared_ua_title)).\
			order_by(orm.asc(orm.uatrains.E.c_date)).first()
	except orm.NoResultFound:
		pass
	except:
		t = None
	return t
def get_s(e, ses):
	s = None
	try:
		prepared_ua_title = e.ua_title.replace(' ', '%').replace('-', '%') if e.ua_title is not None else ''
		s = ses.query(orm.uatrains.E).\
			filter(orm.and_(orm.uatrains.E.etype == e.etype,
				orm.uatrains.E.oid == e.oid, orm.uatrains.E.ua_title.ilike(prepared_ua_title))).\
			order_by(orm.asc(orm.uatrains.E.c_date)).first()
	except orm.NoResultFound:
		try:
			if e.oid >= 20000:
				s = ses.query(orm.uatrains.E).\
					filter(orm.and_(orm.uatrains.E.etype == e.etype,
						orm.uatrains.E.oid < 20000, orm.uatrains.E.ua_title.ilike(prepared_ua_title))).\
					order_by(orm.asc(orm.uatrains.E.c_date)).first()
			elif e.oid < 20000:
				s = ses.query(orm.uatrains.E).\
					filter(orm.and_(orm.uatrains.E.etype == e.etype,
						orm.uatrains.E.oid >= 20000, orm.uatrains.E.ua_title.ilike(prepared_ua_title))).\
					order_by(orm.asc(orm.uatrains.E.c_date)).first()
		except orm.NoResultFound:
			pass
	except:
		s = None
	return s
def get_ts(ts, ses):
	db_ts = None
	try:
		db_ts = ses.query(orm.uatrains.TrainStation).\
			filter(orm.and_(orm.uatrains.TrainStation.t_id == ts.t_id, orm.uatrains.TrainStation.s_id == ts.s_id,
				orm.uatrains.TrainStation.order == ts.order)).\
			one()
	except orm.NoResultFound:
		pass
	except:
		db_ts = None
	return db_ts
def clear_raw_str(raw_str):
	m = re.search(r'\r\n[a-z0-9]*\r\n', raw_str)
	if m:
		return raw_str.replace(m.group(0), '')
	return raw_str

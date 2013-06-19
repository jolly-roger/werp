import redis
import traceback

from ... import orm

def is_not_empty(e):
	ret = False
	if (e.ua_title is not None or e.ru_title is not None or e.en_title is not None) and e.value is not None and \
		e.oid is not None:
		ret = True
	return ret
def has_all_data(e):
	ret = False
	if e.ua_title is not None or e.ru_title is not None or e.en_title is not None or e.value is not None or \
		e.oid is not None:
		ret = True
	return ret
def get_t(e, ses):
	t = None
	try:
		prepared_ua_title = e.ua_title if e.ua_title is not None else ''
		prepared_ru_title = e.ru_title if e.ru_title is not None else ''
		prepared_en_title = e.en_title if e.en_title is not None else ''
		t = ses.query(orm.E).\
			filter(orm.and_(orm.E.etype == e.etype, orm.E.oid == e.oid,
				orm.E.value == e.value)).\
			filter(orm.or_(orm.E.ua_title == prepared_ua_title,
				orm.E.ru_title == prepared_ru_title,
				orm.E.en_title == prepared_en_title)).\
			one()
	except orm.NoResultFound:
		pass
	except:
		t = None
	return t
def get_s(e, ses):
	s = None
	try:
		prepared_ua_title = e.ua_title.replace(' ', '%').replace('-', '%') if e.ua_title is not None else ''
		prepared_ru_title = e.ru_title.replace(' ', '%').replace('-', '%') if e.ru_title is not None else ''
		prepared_en_title = e.en_title.replace(' ', '%').replace('-', '%') if e.en_title is not None else ''
		s = ses.query(orm.E).\
			filter(orm.and_(orm.E.etype == e.etype, orm.E.oid == e.oid)).\
			filter(orm.or_(orm.E.ua_title.ilike(prepared_ua_title),
				orm.E.ru_title.ilike(prepared_ru_title),
				orm.E.en_title.ilike(prepared_en_title))).\
			one()
	except orm.NoResultFound:
		pass
	except:
		s = None
	return s
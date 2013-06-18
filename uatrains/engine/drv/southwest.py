from lxml import etree
import traceback
import urllib.parse
import logging
import redis

from ...common import etype
from ... import orm
from .. import trainstation

from werp.common import red_keys
from werp.common import sockets

logger = logging.getLogger('werp_error.uatrains_spider')

charset = 'cp1251'
domain = 'http://www.swrailway.gov.ua'
ua_url = 'http://www.swrailway.gov.ua/timetable/eltrain/?tid=(tid)&lng=_ua'
ru_url = 'http://www.swrailway.gov.ua/timetable/eltrain/?tid=(tid)&lng=_ru'
en_url = 'http://www.swrailway.gov.ua/timetable/eltrain/?tid=(tid)&lng=_en'
xttitle = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[2]/b'
xtvalue = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[3]/b'
xtperiod = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[3]/text()'
xts = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr'

red = redis.StrictRedis(unix_socket_path=sockets.redis)

def from_remote(ua_dom_tree, ru_dom_tree, en_dom_tree, tid):
	raw_ua_t_title = None
	raw_ru_t_title = None
	raw_en_t_title = None
	raw_ua_period = None
	raw_ru_period = None
	raw_en_period = None
	raw_t_value = None
	if ua_dom_tree is not None:
		raw_ua_t_title = ua_dom_tree.xpath(xttitle)
		raw_ua_period = ua_dom_tree.xpath(xtperiod)
		raw_t_value = ua_dom_tree.xpath(xtvalue)
	if ru_dom_tree is not None:
		raw_ru_t_title = ru_dom_tree.xpath(xttitle)
		raw_ru_period = ru_dom_tree.xpath(xtperiod)
	if en_dom_tree is not None:
		raw_en_t_title = en_dom_tree.xpath(xttitle)
		raw_en_period = en_dom_tree.xpath(xtperiod)
	ua_t_title = None
	ru_t_title = None
	en_t_title = None
	ua_period = None
	ru_period = None
	en_period = None
	value = None
	if raw_ua_t_title is not None and len(raw_ua_t_title) > 0:
		if raw_ua_t_title[0].text is not None and \
			raw_ua_t_title[0].text.strip() != '' and raw_ua_t_title[0].text.strip() != '–':
			ua_t_title = raw_ua_t_title[0].text.strip()
		elif len(raw_ua_t_title[0]) > 0 and raw_ua_t_title[0][0].text is not None and \
			raw_ua_t_title[0][0].text.strip() != '' and raw_ua_t_title[0][0].text.strip() != '–':
			ua_t_title = raw_ua_t_title[0][0].text.strip()
	if raw_ru_t_title is not None and len(raw_ru_t_title) > 0:
		if raw_ru_t_title[0].text is not None and \
			raw_ru_t_title[0].text.strip() != '' and raw_ru_t_title[0].text.strip() != '–':
			ru_t_title = raw_ru_t_title[0].text.strip()
		elif len(raw_ru_t_title[0]) > 0 and raw_ru_t_title[0][0].text is not None and \
			raw_ru_t_title[0][0].text.strip() != '' and raw_ru_t_title[0][0].text.strip() != '–':
			ru_t_title = raw_ru_t_title[0][0].text.strip()
	if raw_en_t_title is not None and len(raw_en_t_title) > 0:
		if raw_en_t_title[0].text is not None and \
			raw_en_t_title[0].text.strip() != '' and raw_en_t_title[0].text.strip() != '–':
			en_t_title = raw_en_t_title[0].text.strip()
		elif len(raw_en_t_title[0]) > 0 and raw_en_t_title[0][0].text is not None and \
			raw_en_t_title[0][0].text.strip() != '' and raw_en_t_title[0][0].text.strip() != '–':
			en_t_title = raw_en_t_title[0][0].text.strip()
	if raw_t_value is not None and len(raw_t_value) > 0 and raw_t_value[0].text is not None and \
		raw_t_value[0].text.strip() != '':
		value = raw_t_value[0].text.strip()
		value_parts = value.split('/')
		if value.startswith('/'):
			value = value[1:]
		if len(value_parts) > 1:
			try:
				int(value_parts[-1])
			except:
				value = '/'.join(value_parts[:len(value_parts) - 1])
	if raw_ua_period is not None and len(raw_ua_period) > 0 and raw_ua_period[-1] is not None and \
		raw_ua_period[-1].strip() != '':
		ua_period = raw_ua_period[-1].strip()
	if raw_ru_period is not None and len(raw_ru_period) > 0 and raw_ru_period[-1] is not None and \
		raw_ru_period[-1].strip() != '':
		ru_period = raw_ru_period[-1].strip()
	if raw_en_period is not None and len(raw_en_period) > 0 and raw_en_period[-1] is not None and \
		raw_en_period[-1].strip() != '':
		en_period = raw_en_period[-1].strip()
	return orm.E(etype.train, value, tid, ua_t_title, ru_t_title, en_t_title, ua_period, ru_period, en_period)
def link_to_station(ua_dom_tree, ru_dom_tree, en_dom_tree, t, ses):
	raw_ua_s_titles = None
	raw_ru_s_titles = None
	raw_en_s_titles = None
	s_count = None
	default_raw_s_titles = None
	if ua_dom_tree is not None:
		raw_ua_s_titles = ua_dom_tree.xpath(xts)
		s_count = len(raw_ua_s_titles)
		default_raw_s_titles = raw_ua_s_titles
	if ru_dom_tree is not None:
		raw_ru_s_titles = ru_dom_tree.xpath(xts)
		if s_count is None:
			s_count = len(raw_ru_s_titles)
		if default_raw_s_titles is None:
			default_raw_s_titles = raw_ru_s_titles
	if en_dom_tree is not None:
		raw_en_s_titles = en_dom_tree.xpath(xts)
		if s_count is None:
			s_count = len(raw_en_s_titles)
		if default_raw_s_titles is None:
			default_raw_s_titles = raw_en_s_titles
	for i in range(s_count):
		if s_count > 0 and i < s_count and len(default_raw_s_titles[i]) >= 4 and \
			default_raw_s_titles[i][0] is not None and \
			len(default_raw_s_titles[i][0].xpath('descendant-or-self::*/text()')) > 0:
			valid_title = ''
			for txt in default_raw_s_titles[i][0].xpath('descendant-or-self::*/text()'):
				if txt.strip() != '':
					valid_title = txt.strip()
			if valid_title != '№':
				ua_s_title = None
				ru_s_title = None
				en_s_title = None
				sid = None
				default_raw_s_title = default_raw_s_titles[i]
				value = None
				if raw_ua_s_titles is not None and len(raw_ua_s_titles) > 0 and i < len(raw_ua_s_titles):
					raw_ua_s_title = raw_ua_s_titles[i]
					if len(raw_ua_s_title) >= 4:
						if len(raw_ua_s_title[1].xpath('descendant-or-self::*/text()')) > 0:
							for txt in raw_ua_s_title[1].xpath('descendant-or-self::*/text()'):
								if txt.strip() != '':
									ua_s_title = txt.strip()
									break
					if ua_s_title is not None:
						if ua_s_title.startswith('пл.'):
							ua_s_title = ua_s_title.replace('пл.', '').strip()
							value = 'пл.'
						elif ua_s_title.startswith('ст.'):
							ua_s_title = ua_s_title.replace('ст.', '').strip()
							value = 'ст.'
						else:
							value = 'ст.'
					if len(raw_ua_s_title[1]) > 0:
						raw_sid_qs = urllib.parse.urlparse(raw_ua_s_title[1][0].get('href'))
						if len(raw_sid_qs.query) > 0:
								raw_sid = urllib.parse.parse_qs(raw_sid_qs.query)
								try:
									sid = int(raw_sid['sid'][0])
								except:
									pass
				if raw_ru_s_titles is not None and len(raw_ru_s_titles) > 0 and i < len(raw_ru_s_titles):
					raw_ru_s_title = raw_ru_s_titles[i]
					if len(raw_ru_s_title) >= 4:
						if len(raw_ru_s_title[1].xpath('descendant-or-self::*/text()')) > 0:
							for txt in raw_ru_s_title[1].xpath('descendant-or-self::*/text()'):
								if txt.strip() != '':
									ru_s_title = txt.strip()
									break
					if ru_s_title is not None:
						if ru_s_title.startswith('пл.'):
							ru_s_title = ru_s_title.replace('пл.', '').strip()
						elif ru_s_title.startswith('ст.'):
							ru_s_title = ru_s_title.replace('ст.', '').strip()
				if raw_en_s_titles is not None and len(raw_en_s_titles) > 0 and i < len(raw_en_s_titles):
					raw_en_s_title = raw_en_s_titles[i]
					if len(raw_en_s_title) >= 4:
						if len(raw_en_s_title[1].xpath('descendant-or-self::*/text()')) > 0:
							for txt in raw_en_s_title[1].xpath('descendant-or-self::*/text()'):
								if txt.strip() != '':
									en_s_title = txt.strip()
									break
					if en_s_title is not None:
						if en_s_title.startswith('pl.'):
							en_s_title = en_s_title.replace('pl.', '').strip()
						elif en_s_title.startswith('st.'):
							en_s_title = en_s_title.replace('st.', '').strip()
				e = orm.E(etype.station, value, sid, ua_s_title, ru_s_title, en_s_title, None, None, None)
				if e is not None:
					if is_not_empty(e):
						if has_all_data(e):
							s = get_s(e, ses)
							if s is None:
								ses.add(e)
								ses.commit()
								s = e
						else:
							red.rpush(red_keys.uatrains_bot_log, 
								('Station has no all data\r\n' + \
								'sid: ' + str(sid) + '\r\n' + \
								'tid: ' + str(t.oid) + '\r\n' + \
								'value: ' + str(value) + '\r\n' + \
								'ua_s_title: ' + str(ua_s_title) + '\r\n' + \
								'ru_s_title: ' + str(ru_s_title) + '\r\n' + \
								'en_s_title: ' + str(en_s_title)).encode('utf-8'))
							raise Exception('Southwest driver station entity has empty fields')
						order = None
						arrival = None
						departure = None
						halt = None
						if len(default_raw_s_title[0].xpath('descendant-or-self::*/text()')) > 0:
							order = int(default_raw_s_title[0].xpath('descendant-or-self::*/text()')[0].strip())
						if len(default_raw_s_title[2].xpath('descendant-or-self::*/text()')) > 0 and \
							default_raw_s_title[2].xpath('descendant-or-self::*/text()')[0].strip() != '–' and \
							default_raw_s_title[3].xpath('descendant-or-self::*/text()')[0].strip() != '-' and \
							default_raw_s_title[2].xpath('descendant-or-self::*/text()')[0].strip() != '':
							arrival = default_raw_s_title[2].xpath('descendant-or-self::*/text()')[0].strip()
						if len(default_raw_s_title[3].xpath('descendant-or-self::*/text()')) > 0 and \
							default_raw_s_title[3].xpath('descendant-or-self::*/text()')[0].strip() != '–' and \
							default_raw_s_title[3].xpath('descendant-or-self::*/text()')[0].strip() != '-' and \
							default_raw_s_title[3].xpath('descendant-or-self::*/text()')[0].strip() != '':
							departure = default_raw_s_title[3].xpath('descendant-or-self::*/text()')[0].strip()
						if len(default_raw_s_title) >= 5 and \
							len(default_raw_s_title[4].xpath('descendant-or-self::*/text()')) > 0 and \
							default_raw_s_title[4].xpath('descendant-or-self::*/text()')[0].strip() != '–' and \
							default_raw_s_title[4].xpath('descendant-or-self::*/text()')[0].strip() != '-' and \
							default_raw_s_title[4].xpath('descendant-or-self::*/text()')[0].strip() != '':
							halt = default_raw_s_title[4].xpath('descendant-or-self::*/text()')[0].strip()
						ts = orm.TrainStation(t.id, s.id, order, arrival, departure, halt)
						if not trainstation.is_added(ts, ses):
							ses.add(ts)
						elif trainstation.is_changed(ts, ses):
							trainstation.load_changes(ts, ses)
						ses.commit()
					else:
						red.rpush(red_keys.uatrains_bot_log, 
								('Station is empty\r\n' + \
								'sid: ' + str(sid) + '\r\n' + \
								'tid: ' + str(t.oid) + '\r\n' + \
								'value: ' + str(value) + '\r\n' + \
								'ua_s_title: ' + str(ua_s_title) + '\r\n' + \
								'ru_s_title: ' + str(ru_s_title) + '\r\n' + \
								'en_s_title: ' + str(en_s_title)).encode('utf-8'))
def get_train_data(tid, ua_dom_tree, ru_dom_tree, en_dom_tree):
	ses = None
	conn = None
	try:
		conn = orm.null_engine.connect()
		ses = orm.sescls(bind=conn)
		e = from_remote(ua_dom_tree, ru_dom_tree, en_dom_tree, tid)
		if e is not None:
			if is_not_empty(e):
				if has_all_data(e):
					t = get_t(e, ses)
					if t is None:
						ses.add(e)
						t = e
					else:
						if t.ua_title is None:
							t.ua_title = e.ua_title
						if t.ru_title is None:
							t.ru_title = e.ru_title
						if t.en_title is None:
							t.en_title = e.en_title
						if e.ua_period is not None:
							t.ua_period = e.ua_period
						if e.ru_period is not None:
							t.ru_period = e.ru_period
						if e.en_period is not None:
							t.en_period = e.en_period
					ses.commit()
					link_to_station(ua_dom_tree, ru_dom_tree, en_dom_tree, t, ses)
				else:
					red.rpush(red_keys.uatrains_bot_log,
						('Train has no all data\r\n' + \
						'tid: ' + str(tid)).encode('utf-8'))
					raise Exception('Southwest driver train entity has empty fields')
		ses.commit()
		ses.close()
		conn.close()
	except Exception as e:
		if ses is not None:
			ses.close()
		if conn is not None:
			conn.close()
		raise e
def get_t(e, ses):
	t = None
	try:
		t = ses.query(orm.E).filter(orm.and_(orm.and_(orm.E.etype == e.etype, orm.E.oid == e.oid),
			orm.E.value == e.value)).\
			filter(orm.or_(orm.or_(orm.or_(orm.E.ua_title == e.ua_title), orm.E.ru_title == e.ru_title),
			orm.E.en_title == e.en_title)).one()
	except orm.NoResultFound:
		pass
	except:
		logger.error(traceback.format_exc())
	return t
def get_s(e, ses):
	s = None
	try:
		s = ses.query(orm.E).filter(orm.and_(orm.E.etype == e.etype, orm.E.oid == e.oid)).\
			filter(orm.or_(orm.or_(orm.or_(orm.E.ua_title == e.ua_title), orm.E.ru_title == e.ru_title),
			orm.E.en_title == e.en_title)).one()
	except orm.NoResultFound:
		pass
	except:
		logger.error(traceback.format_exc())
	return s
def is_not_empty(e):
	ret = False
	if e.ua_title is not None and e.ru_title is not None and e.en_title is not None and e.value is not None and \
		e.oid is not None:
		ret = True
	return ret
def has_all_data(e):
	ret = False
	if e.ua_title is not None or e.ru_title is not None or e.en_title is not None or e.value is not None or \
		e.oid is not None:
		ret = True
	return ret
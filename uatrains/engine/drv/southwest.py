import traceback
import urllib.parse
from lxml import etree
import io
import logging

from ...common import etype
from ... import orm
from .. import trainstation

logger = logging.getLogger('werp_error.uatrains_spider')

chatset = 'cp1251'
domain = 'http://www.swrailway.gov.ua'
ua_url = 'http://www.swrailway.gov.ua/timetable/eltrain/?tid=(tid)&lng=_ua'
ru_url = 'http://www.swrailway.gov.ua/timetable/eltrain/?tid=(tid)&lng=_ru'
en_url = 'http://www.swrailway.gov.ua/timetable/eltrain/?tid=(tid)&lng=_en'
xttitle = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[2]/b'
xtvalue = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[3]/b'
xtperiod = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[3]/text()'
xts = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr'


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
	if raw_ua_period is not None and len(raw_ua_period) > 0 and raw_ua_period[0] is not None and \
		raw_ua_period[0].strip() != '':
		ua_period = raw_ua_period[0].strip()
		period_parts = ua_period.split('/')
		if len(period_parts) > 1:
			try:
				int(period_parts[-1])
			except:
				ua_period = period_parts[-1]
	if raw_ru_period is not None and len(raw_ru_period) > 0 and raw_ru_period[0] is not None and \
		raw_ru_period[0].strip() != '':
		ru_period = raw_ru_period[0].strip()
		period_parts = ru_period.split('/')
		if len(period_parts) > 1:
			try:
				int(period_parts[-1])
			except:
				ru_period = period_parts[-1]
	if raw_en_period is not None and len(raw_en_period) > 0 and raw_en_period[0] is not None and \
		raw_en_period[0].strip() != '':
		en_period = raw_en_period[0].strip()
		period_parts = en_period.split('/')
		if len(period_parts) > 1:
			try:
				int(period_parts[-1])
			except:
				en_period = period_parts[-1]
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
					if not is_empty(e):
						s = None
						if not is_s_added(e, ses):
							ses.add(e)
							ses.commit()
						else:
							oe = get_s(e, ses)
							s = oe
						if s is None:
							s = e
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
						if len(default_raw_s_title) >= 4 and \
							len(default_raw_s_title[4].xpath('descendant-or-self::*/text()')) > 0 and \
							default_raw_s_title[4].xpath('descendant-or-self::*/text()')[0].strip() != '–' and \
							default_raw_s_title[3].xpath('descendant-or-self::*/text()')[0].strip() != '-' and \
							default_raw_s_title[4].xpath('descendant-or-self::*/text()')[0].strip() != '':
							halt = default_raw_s_title[4].xpath('descendant-or-self::*/text()')[0].strip()
						ts = orm.TrainStation(t.id, s.id, order, arrival, departure, halt)
						if not trainstation.is_added(ts, ses):
							ses.add(ts)
						elif trainstation.is_changed(ts, ses):
							trainstation.load_changes(ts, ses)
						ses.commit()
def get_train_data(tid, ua_res_data, ru_res_data, en_res_data):
	ses = None
	conn = None
	try:
		conn = orm.null_engine.connect()
		ses = orm.sescls(bind=conn)
		e = None
		parser = etree.HTMLParser()
		ua_dom_tree = etree.parse(io.StringIO(ua_res_data), parser)
		ru_dom_tree = etree.parse(io.StringIO(ru_res_data), parser)
		en_dom_tree = etree.parse(io.StringIO(en_res_data), parser)
		e = from_remote(ua_dom_tree, ru_dom_tree, en_dom_tree, tid)
		if e is not None:
			if not is_empty(e):
				t = None
				if not is_t_added(e, ses):
					ses.add(e)
				else:
					oe = get_t(e, ses)
					oe.ua_period = e.ua_period
					oe.ru_period = e.ru_period
					oe.en_period = e.en_period
					t = oe
				ses.commit()
				if t is None:
					t = e
				link_to_station(ua_dom_tree, ru_dom_tree, en_dom_tree, t, ses)
		ses.commit()
		ses.close()
		conn.close()
	except Exception as e:
		logger.fatal('Train id: ' + str(tid) + ' For more details see following record.')
		logger.fatal(traceback.format_exc())
		if ses is not None:
			ses.commit()
			ses.close()
		if conn is not None:
			conn.close()
		raise e
def get_t(e, ses):
	t = None
	try:
		t = ses.query(orm.E).filter(orm.and_(orm.and_(orm.and_(orm.and_(orm.and_(
			orm.E.etype == e.etype, orm.E.oid == e.oid),
			orm.E.ua_title == e.ua_title), orm.E.ru_title == e.ru_title),
			orm.E.en_title == e.en_title), orm.E.value == e.value)).one()
	except:
		logger.error(traceback.format_exc())
	return t
def get_s(e, ses):
	s = None
	try:
		s = ses.query(orm.E).filter(orm.and_(orm.and_(orm.and_(orm.and_(
			orm.E.etype == e.etype, orm.E.oid == e.oid),
			orm.E.ua_title == e.ua_title), orm.E.ru_title == e.ru_title),
			orm.E.en_title == e.en_title)).one()
	except:
		logger.error(traceback.format_exc())
	return s
def is_t_added(t, ses):
	ret = False
	try:
		ses.query(orm.E).filter(orm.and_(orm.and_(orm.and_(orm.and_(orm.and_(
			orm.E.etype == t.etype, orm.E.oid == t.oid),
			orm.E.ua_title == t.ua_title), orm.E.ru_title == t.ru_title),
			orm.E.en_title == t.en_title), orm.E.value == t.value)).one()
		ret = True
	except orm.NoResultFound:
		pass
	return ret
def is_s_added(s, ses):
	ret = False
	try:
		ses.query(orm.E).filter(orm.and_(orm.and_(orm.and_(orm.and_(
			orm.E.etype == s.etype, orm.E.oid == s.oid),
			orm.E.ua_title == s.ua_title), orm.E.ru_title == s.ru_title),
			orm.E.en_title == s.en_title)).one()
		ret = True
	except orm.NoResultFound:
		pass
	return ret
def is_empty(e):
	ret = False
	if e.ua_title is None and e.ru_title is None and e.en_title is None:
		ret = True
	return ret
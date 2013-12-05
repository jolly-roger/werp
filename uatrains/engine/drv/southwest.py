import urllib.parse
import datetime
import traceback

from ...common import etype
from . import common

from werp import orm
from werp.uatrains import bot
from werp.uatrains.engine import triggers

name = 'southwest'
charset = 'cp1251'
domain = 'http://www.swrailway.gov.ua'
ua_url = 'http://www.swrailway.gov.ua/timetable/eltrain/?tid=(tid)&lng=_ua'
xtattrs = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[3]'
xttitle = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[2]/b'
xtvalue = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[3]/b'
xtperiod = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr[2]/td[3]/text()'
xts = '/html/body/table/tr[2]/td/table/tr[3]/td[4]/table/tr/td/table/tr[2]/td/center/table/tr/td/table/tr'


def from_remote(ua_dom_tree, tid):
	raw_ua_t_title = None
	raw_ua_period = None
	raw_t_value = None
	raw_t_attrs = None
	if ua_dom_tree is not None:
		raw_ua_t_title = ua_dom_tree.xpath(xttitle)
		raw_ua_period = ua_dom_tree.xpath(xtperiod)
		raw_t_value = ua_dom_tree.xpath(xtvalue)
		raw_t_attrs = ua_dom_tree.xpath(xtattrs)
	ua_t_title = None
	ua_period = None
	value = None
	from_date = None
	to_date = None
	if raw_ua_t_title is not None and len(raw_ua_t_title) > 0:
		if raw_ua_t_title[0].text is not None and \
			raw_ua_t_title[0].text.strip() != '' and raw_ua_t_title[0].text.strip() != '–':
			ua_t_title = raw_ua_t_title[0].text.strip()
		elif len(raw_ua_t_title[0]) > 0 and raw_ua_t_title[0][0].text is not None and \
			raw_ua_t_title[0][0].text.strip() != '' and raw_ua_t_title[0][0].text.strip() != '–':
			ua_t_title = raw_ua_t_title[0][0].text.strip()
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
	if raw_t_attrs is not None and len(raw_t_attrs) > 0:
		raw_dates = raw_t_attrs[0].xpath('img/@title')
		if len(raw_dates) > 0:
			raw_dates_parts = common.clear_raw_str(raw_dates[0]).split(' ')
			if len(raw_dates_parts) > 1 and raw_dates_parts[1].strip() != '':
				raw_from_date = raw_dates_parts[1].strip()
				if raw_from_date != '0000-00-00':
					from_date = datetime.datetime.strptime(raw_from_date, '%Y-%m-%d').date()
			if len(raw_dates_parts) > 3 and raw_dates_parts[3].strip() != '':
				raw_to_date = raw_dates_parts[3].strip()
				if raw_to_date != '0000-00-00':
					to_date = datetime.datetime.strptime(raw_to_date, '%Y-%m-%d').date()
	if raw_ua_period is not None and len(raw_ua_period) > 0 and raw_ua_period[-1] is not None and \
		raw_ua_period[-1].strip() != '':
		ua_period = raw_ua_period[-1].strip()
	return orm.uatrains.E(etype.train, value, tid, ua_t_title, None, None, ua_period, None, None,
		from_date, to_date)
def link_to_station(ua_dom_tree, t, ses):
	raw_ua_s_titles = None
	s_count = None
	default_raw_s_titles = None
	if ua_dom_tree is not None:
		raw_ua_s_titles = ua_dom_tree.xpath(xts)
		s_count = len(raw_ua_s_titles)
		default_raw_s_titles = raw_ua_s_titles
	else:
		bot.logger.error('link_to_station: southwest ua_dom_tree is None\r\n')
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
				sid = None
				default_raw_s_title = default_raw_s_titles[i]
				value = None
				if raw_ua_s_titles is not None and len(raw_ua_s_titles) > 0 and i < len(raw_ua_s_titles):
					raw_ua_s_title = raw_ua_s_titles[i]
					if len(raw_ua_s_title) >= 4:
						if len(raw_ua_s_title[1].xpath('a/b/text() | a[not(child::b)]/text()')) > 0:
							for txt in raw_ua_s_title[1].xpath('a/b/text() | a[not(child::b)]/text()'):
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
									if 'sid' in raw_sid and raw_sid['sid'][0] != '':
										sid = int(common.clear_raw_str(raw_sid['sid'][0]))
								except:
									bot.logger.error('sid parse error\r\n' +\
										'raw sid: ' + str(raw_sid_qs.query) + '\r\n\r\n' +\
										traceback.format_exc())
				else:
					if raw_ua_s_titles is None:
						bot.logger.error('link_to_station: southwest raw_ua_s_titles is None\r\n' +\
							'tid: ' + str(t.oid) + '\r\n' +\
							'sid: ' + str(sid) + '\r\n')
					elif len(raw_ua_s_titles) == 0:
						bot.logger.error('link_to_station: southwest len raw_ua_s_titles is 0\r\n' +\
							'tid: ' + str(t.oid) + '\r\n' +\
							'sid: ' + str(sid) + '\r\n')
					else:
						bot.logger.error('link_to_station: southwest raw_ua_s_titles is incorrect\r\n' +\
							'tid: ' + str(t.oid) + '\r\n' +\
							'sid: ' + str(sid) + '\r\n')
				e = orm.uatrains.E(etype.station, value, sid, ua_s_title, None, None, None, None, None)
				if e is not None:
					if common.is_not_empty(e):
						s = common.get_s(e, ses)
						if s is None:
							if common.e_has_all_data(e):
								ses.add(e)
								ses.commit()
								s = e
								triggers.e.add_history(ses, s, orm.uatrains.htype.insert)
							else:
								bot.logger.error('Station has no all data\r\n' + \
									'sid: ' + str(sid) + '\r\n' + \
									'tid: ' + str(t.oid) + '\r\n' + \
									'value: ' + str(value) + '\r\n' + \
									'ua_s_title: ' + str(ua_s_title) + '\r\n')
								raise Exception('Southwest driver station entity has empty fields')
						if s is not None:
							if not common.e_has_all_data(s):
								if s.ua_title is None:
									s.ua_title = e.ua_title
								ses.commit()
								triggers.e.add_history(ses, s, orm.uatrains.htype.update)
							order = None
							arrival = None
							departure = None
							halt = None
							if len(default_raw_s_title[0].xpath('font/text()')) > 0:
								order = int(common.clear_raw_str(default_raw_s_title[0].xpath('font/text()')[0]).strip())
							if len(default_raw_s_title[2].xpath('text()')) > 0 and \
								default_raw_s_title[2].xpath('text()')[0].strip() != '–' and \
								default_raw_s_title[2].xpath('text()')[0].strip() != '-' and \
								default_raw_s_title[2].xpath('text()')[0].strip() != '':
								arrival = default_raw_s_title[2].xpath('text()')[0].strip()
							if len(default_raw_s_title[3].xpath('text()')) > 0 and \
								default_raw_s_title[3].xpath('text()')[0].strip() != '–' and \
								default_raw_s_title[3].xpath('text()')[0].strip() != '-' and \
								default_raw_s_title[3].xpath('text()')[0].strip() != '':
								departure = default_raw_s_title[3].xpath('text()')[0].strip()
							ts = orm.uatrains.TrainStation(t.id, s.id, order, arrival, departure, halt)
							if ts is not None:
								if common.ts_has_all_data(ts):
									db_ts = common.get_ts(ts, ses)
									if db_ts is None:
										ses.add(ts)
									else:
										db_ts.arrival = ts.arrival
										db_ts.departure = ts.departure
										db_ts.halt = ts.halt
										db_ts.date_from = ts.date_from
										db_ts.date_to = ts.date_to
									ses.commit()
					else:
						if sid is not None or \
							value is not None or \
							ua_s_title is not None:
							bot.logger.error('Station is empty\r\n' + \
								'sid: ' + str(sid) + '\r\n' + \
								'tid: ' + str(t.oid) + '\r\n' + \
								'value: ' + str(value) + '\r\n' + \
								'ua_s_title: ' + str(ua_s_title) + '\r\n')

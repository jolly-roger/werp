import urllib.parse
import traceback

from ...common import etype
from . import common

from werp import orm
from werp.uatrains import bot
from werp.uatrains.engine import triggers

name = 'passengers'
charset = 'utf-8'
domain = 'http://www.uz.gov.ua'
ua_url = 'http://www.uz.gov.ua/passengers/timetables/?ntrain=(tid)&by_id=1'
xtattrs = '/html/body'
xttitle = '/html/body/div/div[2]/div[2]/div[2]/div[2]/div[3]/table[1]/tbody/tr/td[1]'
xtvalue = '/html/body/div/div[2]/div[2]/div[2]/div[2]/div[3]/table[1]/tbody/tr/td[2]'
xtperiod = '/html/body/div/div[2]/div[2]/div[2]/div[2]/div[3]/table[1]/tbody/tr/td[3]/text()'
xts = '/html/body/div/div[2]/div[2]/div[2]/div[2]/div[3]/table[2]/tbody/tr'


def from_remote(ua_dom_tree, tid):
	raw_ua_t_title = None
	raw_ua_period = None
	raw_ua_t_value = None
	if ua_dom_tree is not None:
		raw_ua_t_title = ua_dom_tree.xpath(xttitle)
		raw_ua_period = ua_dom_tree.xpath(xtperiod)
		raw_ua_t_value = ua_dom_tree.xpath(xtvalue)
	ua_t_title = None
	ua_period = None
	value = None
	if raw_ua_t_title is not None and len(raw_ua_t_title) > 0:
		if raw_ua_t_title[0].text is not None and \
			raw_ua_t_title[0].text.strip() != '' and raw_ua_t_title[0].text.strip() != '–':
			ua_t_title = raw_ua_t_title[0].text.strip()
		elif len(raw_ua_t_title[0]) > 0 and raw_ua_t_title[0][0].text is not None and \
			raw_ua_t_title[0][0].text.strip() != '' and raw_ua_t_title[0][0].text.strip() != '–':
			ua_t_title = raw_ua_t_title[0][0].text.strip()
		if raw_ua_t_value is not None and len(raw_ua_t_value) > 0 and raw_ua_t_value[0].text is not None and \
			raw_ua_t_value[0].text.strip() != '':
			ua_value = raw_ua_t_value[0].text.strip()
			value_parts = ua_value.split(' ')
			if len(value_parts) > 1:
				value = value_parts[0]
				value_desc = ' '.join(value_parts[1:len(value_parts)])
				ua_t_title = ua_t_title + \
					' (' + value_desc.replace('"', '').replace('(', '').replace(')', '').strip() + ')'
			else:
				value = ua_value
	if raw_ua_period is not None and len(raw_ua_period) > 0 and raw_ua_period[0] is not None and \
		raw_ua_period[0].strip() != '':
		ua_period = raw_ua_period[0].strip()
	return orm.uatrains.E(etype.ptrain, value, tid, ua_t_title, None, None, ua_period, None, None)
def link_to_station(ua_dom_tree, t, ses):
	raw_ua_s_titles = None
	s_count = None
	default_raw_s_titles = None
	if ua_dom_tree is not None:
		raw_ua_s_titles = ua_dom_tree.xpath(xts)
		s_count = len(raw_ua_s_titles)
		default_raw_s_titles = raw_ua_s_titles
	else:
		bot.logger.error('link_to_station: passengers ua_dom_tree is None\r\n')
	for i in range(s_count):
		if s_count > 0 and i < s_count and len(default_raw_s_titles[i]) >= 3 and \
			default_raw_s_titles[i][0] is not None and \
			len(default_raw_s_titles[i][0].xpath('descendant-or-self::*/text()')) > 0:
			valid_title = ''
			for txt in default_raw_s_titles[i][0].xpath('descendant-or-self::*/text()'):
				if txt.strip() != '':
					valid_title = txt.strip()
			if valid_title.lower() != 'станція':
				ua_s_title = None
				sid = None
				default_raw_s_title = default_raw_s_titles[i]
				value = None
				if raw_ua_s_titles is not None and len(raw_ua_s_titles) > 0 and i < len(raw_ua_s_titles):
					raw_ua_s_title = raw_ua_s_titles[i]
					if len(raw_ua_s_title) >= 3:
						if len(raw_ua_s_title[0].xpath('descendant-or-self::*/text()')) > 0:
							for txt in raw_ua_s_title[0].xpath('descendant-or-self::*/text()'):
								if txt.strip() != '':
									ua_s_title = txt.strip()
									break
					if ua_s_title is not None:
							value = 'ст.'
					if len(raw_ua_s_title[0]) > 0:
						raw_sid_qs = urllib.parse.urlparse(raw_ua_s_title[0][0].get('href'))
						if len(raw_sid_qs.query) > 0:
								raw_sid = urllib.parse.parse_qs(raw_sid_qs.query)
								try:
									if 'station' in raw_sid and raw_sid['station'][0] != '':
										sid = int(common.clear_raw_str(raw_sid['station'][0]))
								except:
									bot.logger.error('sid parse error\r\n' +\
										'raw sid: ' + str(raw_sid_qs.query) + '\r\n\r\n' +\
										traceback.format_exc())
				else:
					if raw_ua_s_titles is None:
						bot.logger.error('link_to_station: passengers raw_ua_s_titles is None\r\n' +\
							'tid: ' + str(t.oid) + '\r\n' +\
							'sid: ' + str(sid) + '\r\n')
					elif len(raw_ua_s_titles) == 0:
						bot.logger.error('link_to_station: passengers len raw_ua_s_titles is 0\r\n' +\
							'tid: ' + str(t.oid) + '\r\n' +\
							'sid: ' + str(sid) + '\r\n')
					else:
						bot.logger.error('link_to_station: passengers raw_ua_s_titles is incorrect\r\n' +\
							'tid: ' + str(t.oid) + '\r\n' +\
							'sid: ' + str(sid) + '\r\n')
				e = orm.uatrains.E(etype.station, value, sid, ua_s_title, None, None)
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
								raise Exception('Passengers driver station entity has empty fields')
						if s is not None:
							if not common.e_has_all_data(s):
								if e.ua_title is not None and s.ua_title != e.ua_title:
									s.ua_title = e.ua_title
									ses.commit()
									triggers.e.add_history(ses, s, orm.uatrains.htype.update)
							order = i
							arrival = None
							departure = None
							halt = None
							if len(default_raw_s_title[1].xpath('descendant-or-self::*/text()')) > 0 and \
								default_raw_s_title[1].xpath('descendant-or-self::*/text()')[0].strip() != '–' and \
								default_raw_s_title[1].xpath('descendant-or-self::*/text()')[0].strip() != '-' and \
								default_raw_s_title[1].xpath('descendant-or-self::*/text()')[0].strip() != '':
								arrival = default_raw_s_title[1].xpath('descendant-or-self::*/text()')[0].strip()
							if len(default_raw_s_title[2].xpath('descendant-or-self::*/text()')) > 0 and \
								default_raw_s_title[2].xpath('descendant-or-self::*/text()')[0].strip() != '–' and \
								default_raw_s_title[2].xpath('descendant-or-self::*/text()')[0].strip() != '-' and \
								default_raw_s_title[2].xpath('descendant-or-self::*/text()')[0].strip() != '':
								departure = default_raw_s_title[2].xpath('descendant-or-self::*/text()')[0].strip()
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

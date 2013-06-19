import urllib.parse

from ...common import etype
from ... import orm
from .. import trainstation
from . import common

from werp.uatrains import bot

name = 'passengers'
charset = 'utf-8'
domain = 'http://www.uz.gov.ua'
ua_url = 'http://www.uz.gov.ua/passengers/timetables/?ntrain=(tid)&by_id=1'
ru_url = 'http://www.uz.gov.ua/passengers/timetables/?ntrain=(tid)&by_id=1'
en_url = 'http://www.uz.gov.ua/en/passengers/timetables/?ntrain=(tid)&by_id=1'
xttitle = '/html/body/div/div[2]/div[2]/div[2]/div[2]/div[3]/table[1]/tbody/tr/td[1]'
xtvalue = '/html/body/div/div[2]/div[2]/div[2]/div[2]/div[3]/table[1]/tbody/tr/td[2]'
xtperiod = '/html/body/div/div[2]/div[2]/div[2]/div[2]/div[3]/table[1]/tbody/tr/td[3]/text()'
xts = '/html/body/div/div[2]/div[2]/div[2]/div[2]/div[3]/table[2]/tbody/tr'


def from_remote(ua_dom_tree, ru_dom_tree, en_dom_tree, tid):
    raw_ua_t_title = None
    raw_ru_t_title = None
    raw_en_t_title = None
    raw_ua_period = None
    raw_ru_period = None
    raw_en_period = None
    raw_ua_t_value = None
    raw_en_t_value = None
    if ua_dom_tree is not None:
        raw_ua_t_title = ua_dom_tree.xpath(xttitle)
        raw_ua_period = ua_dom_tree.xpath(xtperiod)
        raw_ua_t_value = ua_dom_tree.xpath(xtvalue)
    if ru_dom_tree is not None:
        raw_ru_t_title = ru_dom_tree.xpath(xttitle)
        raw_ru_period = ru_dom_tree.xpath(xtperiod)
        raw_ru_t_value = ru_dom_tree.xpath(xtvalue)
    if en_dom_tree is not None:
        raw_en_t_title = en_dom_tree.xpath(xttitle)
        raw_en_period = en_dom_tree.xpath(xtperiod)
        raw_en_t_value = en_dom_tree.xpath(xtvalue)
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
    if raw_ru_t_title is not None and len(raw_ru_t_title) > 0:
        if raw_ru_t_title[0].text is not None and \
            raw_ru_t_title[0].text.strip() != '' and raw_ru_t_title[0].text.strip() != '–':
            ru_t_title = raw_ru_t_title[0].text.strip()
        elif len(raw_ru_t_title[0]) > 0 and raw_ru_t_title[0][0].text is not None and \
            raw_ru_t_title[0][0].text.strip() != '' and raw_ru_t_title[0][0].text.strip() != '–':
            ru_t_title = raw_ru_t_title[0][0].text.strip()
        if raw_ru_t_value is not None and len(raw_ru_t_value) > 0 and raw_ru_t_value[0].text is not None and \
            raw_ru_t_value[0].text.strip() != '':
            ru_value = raw_ru_t_value[0].text.strip()
            value_parts = ru_value.split(' ')
            if len(value_parts) > 1:
                value_desc = ' '.join(value_parts[1:len(value_parts)])
                ru_t_title = ru_t_title + \
                    ' (' + value_desc.replace('"', '').replace('(', '').replace(')', '').strip() + ')'
    if raw_en_t_title is not None and len(raw_en_t_title) > 0:
        if raw_en_t_title[0].text is not None and \
            raw_en_t_title[0].text.strip() != '' and raw_en_t_title[0].text.strip() != '–':
            en_t_title = raw_en_t_title[0].text.strip()
        elif len(raw_en_t_title[0]) > 0 and raw_en_t_title[0][0].text is not None and \
            raw_en_t_title[0][0].text.strip() != '' and raw_en_t_title[0][0].text.strip() != '–':
            en_t_title = raw_en_t_title[0][0].text.strip()
        if raw_en_t_value is not None and len(raw_en_t_value) > 0 and raw_en_t_value[0].text is not None and \
            raw_en_t_value[0].text.strip() != '':
            en_value = raw_en_t_value[0].text.strip()
            value_parts = en_value.split(' ')
            if len(value_parts) > 1:
                value_desc = ' '.join(value_parts[1:len(value_parts)])
                en_t_title = en_t_title + \
                    ' (' + value_desc.replace('"', '').replace('(', '').replace(')', '').strip() + ')'
    if raw_ua_period is not None and len(raw_ua_period) > 0 and raw_ua_period[0] is not None and \
        raw_ua_period[0].strip() != '':
        ua_period = raw_ua_period[0].strip()
    if raw_ru_period is not None and len(raw_ru_period) > 0 and raw_ru_period[0] is not None and \
        raw_ru_period[0].strip() != '':
        ru_period = raw_ru_period[0].strip()
    if raw_en_period is not None and len(raw_en_period) > 0 and raw_en_period[0] is not None and \
        raw_en_period[0].strip() != '':
        en_period = raw_en_period[0].strip()
    return orm.E(etype.ptrain, value, tid, ua_t_title, ru_t_title, en_t_title, ua_period, ru_period, en_period)
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
		if s_count > 0 and i < s_count and len(default_raw_s_titles[i]) >= 3 and \
			default_raw_s_titles[i][0] is not None and \
			len(default_raw_s_titles[i][0].xpath('descendant-or-self::*/text()')) > 0:
			valid_title = ''
			for txt in default_raw_s_titles[i][0].xpath('descendant-or-self::*/text()'):
				if txt.strip() != '':
					valid_title = txt.strip()
			if valid_title.lower() != 'станція':
				ua_s_title = None
				ru_s_title = None
				en_s_title = None
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
									sid = int(raw_sid['station'][0])
								except:
									pass
				if raw_ru_s_titles is not None and len(raw_ru_s_titles) > 0 and i < len(raw_ru_s_titles):
					raw_ru_s_title = raw_ru_s_titles[i]
					if len(raw_ru_s_title) >= 3:
						if len(raw_ru_s_title[0].xpath('descendant-or-self::*/text()')) > 0:
							for txt in raw_ru_s_title[0].xpath('descendant-or-self::*/text()'):
								if txt.strip() != '':
									ru_s_title = txt.strip()
									break
				if raw_en_s_titles is not None and len(raw_en_s_titles) > 0 and i < len(raw_en_s_titles):
					raw_en_s_title = raw_en_s_titles[i]
					if len(raw_en_s_title) >= 3:
						if len(raw_en_s_title[0].xpath('descendant-or-self::*/text()')) > 0:
							for txt in raw_en_s_title[0].xpath('descendant-or-self::*/text()'):
								if txt.strip() != '':
									en_s_title = txt.strip()
									break
				e = orm.E(etype.station, value, sid, ua_s_title, ru_s_title, en_s_title, None, None, None)
				if e is not None:
					if common.is_not_empty(e):
						if common.has_all_data(e):
							s = common.get_s(e, ses)
							if s is None:
								ses.add(e)
								ses.commit()
								s = e
						else:
							bot.logger.error('Station has no all data\r\n' + \
								'sid: ' + str(sid) + '\r\n' + \
								'tid: ' + str(t.oid) + '\r\n' + \
								'value: ' + str(value) + '\r\n' + \
								'ua_s_title: ' + str(ua_s_title) + '\r\n' + \
								'ru_s_title: ' + str(ru_s_title) + '\r\n' + \
								'en_s_title: ' + str(en_s_title))
							raise Exception('Passengers driver station entity has empty fields')
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
						ts = orm.TrainStation(t.id, s.id, order, arrival, departure, halt)
						if not trainstation.is_added(ts, ses):
							ses.add(ts)
						elif trainstation.is_changed(ts, ses):
							trainstation.load_changes(ts, ses)
						ses.commit()
					else:
						bot.logger.error('Station is empty\r\n' + \
							'sid: ' + str(sid) + '\r\n' + \
							'tid: ' + str(t.oid) + '\r\n' + \
							'value: ' + str(value) + '\r\n' + \
							'ua_s_title: ' + str(ua_s_title) + '\r\n' + \
							'ru_s_title: ' + str(ru_s_title) + '\r\n' + \
							'en_s_title: ' + str(en_s_title))
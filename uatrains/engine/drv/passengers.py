import traceback
import urllib.parse
from lxml import etree
import io
import logging

from ...common import etype
from ... import orm
from .. import trainstation

logger = logging.getLogger('werp_error.uatrains_spider')

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
                        if s.id is not None:
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
		t = ses.query(orm.E).filter(orm.and_(orm.and_(orm.E.etype == t.etype, orm.E.oid == t.oid), orm.E.value == t.value)).\
			filter(orm.or_(orm.or_(orm.or_(orm.E.ua_title == t.ua_title), orm.E.ru_title == t.ru_title),
			orm.E.en_title == t.en_title)).one()
	except:
		logger.error(traceback.format_exc())
	return t
def get_s(e, ses):
	s = None
	try:
		prepared_ua_title = s.ua_title.replace(' ', '%').replace('-', '%')
		prepared_ru_title = s.ru_title.replace(' ', '%').replace('-', '%')
		prepared_en_title = s.en_title.replace(' ', '%').replace('-', '%')
		s = ses.query(orm.E).filter(orm.and_(orm.E.etype == s.etype, orm.E.value == s.value)).\
			filter(orm.or_(orm.or_(orm.E.ua_title.ilike(prepared_ua_title, orm.E.ru_title.ilike(prepared_ru_title))),
			orm.E.en_title.ilike(prepared_en_title))).one()
	except:
		logger.info(str(e.value) + ' ' + str(e.ua_title))
		logger.error(traceback.format_exc())
		s = None
	return s
def is_t_added(t, ses):
	ret = False
	try:
		ses.query(orm.E).filter(orm.and_(orm.and_(orm.E.etype == t.etype, orm.E.oid == t.oid), orm.E.value == t.value)).\
			filter(orm.or_(orm.or_(orm.or_(orm.E.ua_title == t.ua_title), orm.E.ru_title == t.ru_title),
			orm.E.en_title == t.en_title)).one()
		ret = True
	except orm.NoResultFound:
		pass
	return ret
def is_s_added(s, ses):
	ret = False
	try:
		prepared_ua_title = s.ua_title.replace(' ', '%').replace('-', '%')
		prepared_ru_title = s.ru_title.replace(' ', '%').replace('-', '%')
		prepared_en_title = s.en_title.replace(' ', '%').replace('-', '%')
		ses.query(orm.E).filter(orm.and_(orm.E.etype == s.etype, orm.E.value == s.value)).\
			filter(orm.or_(orm.or_(orm.E.ua_title.ilike(prepared_ua_title, orm.E.ru_title.ilike(prepared_ru_title))),
			orm.E.en_title.ilike(prepared_en_title))).one()
		ret = True
	except orm.NoResultFound:
		pass
	except:
		logger.info(str(s.value) + ' ' + str(s.ua_title))
		logger.error(traceback.format_exc())
		ret = True
	return ret
def is_empty(e):
	ret = False
	if e.ua_title is None and e.ru_title is None and e.en_title is None:
		ret = True
	return ret  




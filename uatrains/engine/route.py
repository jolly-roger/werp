#import datetime
#import traceback
#import urllib.request
#import urllib.parse
#from lxml import etree
#import io
#import logging
#
#
#from .lng import lngs
#from ..common import etype
#from .. import orm
#from . import routetrain
#from . import src
#
#
#logger = logging.getLogger('werp_error.uatrains_spider')
#railway_id = 0
#
#
#def is_added(route, ses):
#	ret = False
#	try:
#		ses.query(orm.Route).filter(orm.Route.rid == route.rid).one()
#		ret = True
#	except orm.NoResultFound:
#		pass
#	return ret
#def is_changed(route, ses):
#	ret = False
#	try:
#		r = ses.query(orm.Route).filter(orm.Route.rid == route.rid).one()
#		if r.title != route.title or r.value != route.value or r.reverse_title != route.reverse_title or \
#			r.reverse_value != route.reverse_value or r.railway_id != route.railway_id:
#			ret = True
#	except Exception:
#		ret = True
#	return ret
#def is_empty(route):
#	if route.title is None and route.value is None and route.rid is None and route.reverse_title is None and \
#		route.reverse_value is None:
#		return True
#	return False
#def is_incorrect(route):
#	if route.title is None or route.value is None:
#		logger.error('Route is incorrect, rid: ' + route.rid)
#		return True
#	return False
#def load_changes(route, ses):
#	r = ses.query(orm.Route).filter(orm.Route.rid == route.rid).one()
#	r.title = route.title
#	r.value = route.value
#	r.reverse_title = route.reverse_title
#	r.reverse_value = route.reverse_value
#	r.railway_id = route.railway_id
#	return r
#def from_remote(rid, dom_tree, lng):
#	rw_id = None
#	has_railway = dom_tree.xpath('/html/body/table/tr[2]/td/center/form/table/tr[3]/td/span/select/option[@selected]')
#	if len(has_railway) > 0:
#		rw_id = railway_id
#	raw_route = dom_tree.xpath('/html/body/table/tr[2]/td/center/table/tr/td/table/tr[2]/td/span/b')
#	raw_reverse_route = dom_tree.xpath('/html/body/table/tr[2]/td/center/table[2]/tr/td/table/tr[2]/td/span/b')
#	r = orm.Route()
#	if len(raw_route) > 0 and raw_route[0].text is not None and raw_route[0].text.strip() != '' and \
#		len(raw_reverse_route) > 0 and raw_reverse_route[0].text is not None and \
#		raw_reverse_route[0].text.strip() != '':
#		title = raw_route[0].text.strip()
#		reverse_title = raw_reverse_route[0].text.strip()
#		r = orm.Route(None, title, title, reverse_title, reverse_title, rw_id)
#	return r
#def link_route_to_train(dom_tree, xpath, rid, ses, is_reverse=False):
#	raw_trains = dom_tree.xpath(xpath)
#	for raw_train in raw_trains:
#		if len(raw_train) > 0 and len(raw_train[0]) > 0:
#			raw_tid_qs = urllib.parse.urlparse(raw_train[0][0].get('href'))
#			if len(raw_tid_qs.query) > 0:
#				raw_tid = urllib.parse.parse_qs(raw_tid_qs.query)
#				tid = int(raw_tid['tid'][0])
#				t = ses.query(orm.Train).filter(orm.Train.tid == tid).one()
#				r = ses.query(orm.Route).filter(orm.Route.rid == rid).one()
#				rt = orm.RouteTrain(r.id, t.id, is_reverse)
#				if not routetrain.is_added(rt, ses):
#					ses.add(rt)
#				elif routetrain.is_changed(rt, ses):
#					routetrain.load_changes(rt, ses)
#				ses.commit()
#def get_route_data(rid):
#	ses = None
#	conn = None
#	try:
#		conn = orm.null_engine.connect()
#		ses = orm.sescls(bind=conn)
#		data_srcs = src.get_data_srcs(ses)
#		for data_src in data_srcs:
#			for lng in lngs:
#				res = urllib.request.urlopen(src.get_route_url(data_src, (rid, lngs['RU'])))
#				res_data = res.read().decode('cp1251')
#				parser = etree.HTMLParser()
#				dom_tree = etree.parse(io.StringIO(res_data), parser)
#				route = from_remote(rid, dom_tree, lng)
#				if is_empty(route):
#					return
#				route.rid = rid
#				if is_incorrect(route):
#					return
#				if not is_added(route, ses):
#					ses.add(route)
#				elif is_changed(route, ses):
#					load_changes(route, ses)
#				ses.commit()
#				link_route_to_train(dom_tree, '/html/body/table/tr[2]/td/center/table[1]/tr/td[2]/div/table/tr[4]/td',
#					rid, ses, False)
#				link_route_to_train(dom_tree, '/html/body/table/tr[2]/td/center/table[1]/tr/td[2]/table/tr[4]/td',
#					rid, ses, False)
#				link_route_to_train(dom_tree, '/html/body/table/tr[2]/td/center/table[2]/tr/td[2]/div/table/tr[4]/td',
#					rid, ses, True)
#				link_route_to_train(dom_tree, '/html/body/table/tr[2]/td/center/table[2]/tr/td[2]/table/tr[4]/td',
#					rid, ses, True)
#				ses.commit()
#		ses.close()
#		conn.close()
#	except Exception:
#		logger.fatal(traceback.format_exc())
#		if ses is not None:
#			ses.commit()
#			ses.close()
#		if conn is not None:
#			conn.close()
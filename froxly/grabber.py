import urllib.request
import urllib.parse
from lxml import etree
import datetime
import time
import io
import re
import traceback
import zmq
import json
import os.path

from werp import orm
from werp import froxly_grabber_log
from werp.common import sockets

if not os.path.exists(sockets.get_socket_path(sockets.froxly_grabber_server)):
    ctx = zmq.Context()
    froxly_grabber_server_socket = ctx.socket(zmq.PUSH)
    froxly_grabber_server_socket.bind(sockets.froxly_grabber_server)
    TRY_COUNT = 11
    url = 'http://www.hidemyass.com/proxy-list/'
    conn = None
    ses = None
    res_data = None
    start_dt = datetime.datetime.now()
    start_time = time.time()
    froxly_grabber_log.info('Started at %s' % (str(start_dt), ))
    try:
        added_fps = []
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        res = None
        try_count = 0
        froxly_data_server_socket = ctx.socket(zmq.REQ)
        froxly_data_server_socket.connect(sockets.froxly_data_server)
        while res is None and try_count < TRY_COUNT:
            try:
                froxly_data_server_socket.send_unicode(
                    json.dumps({'method': 'request', 'params': {'url': url, 'charset': 'utf-8'}}))
                res = json.loads(froxly_data_server_socket.recv_unicode())
                if res['result']['http_status'] == 200:
                    res_data = res['result']['data']
                else:
                    res = None
            except:
                res = None
            try_count = try_count + 1
            if try_count >= TRY_COUNT:
                froxly_grabber_log.error(str(TRY_COUNT) + ' tries have failed.')
                end_time = time.time()
                exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
                froxly_grabber_log.info('Finished at %s, duration is %s \n\n' % (str(start_dt), str(exec_delta)))
        html_parser = etree.HTMLParser()
        dom_tree = etree.parse(io.StringIO(res_data), html_parser)
        raw_proxies = dom_tree.xpath('/html/body/div/div/table/tr')
        for raw_proxy in raw_proxies:
            try:
                raw_ip = etree.tostring(raw_proxy[1]).decode('utf-8')
                raw_ip_style_text = raw_proxy[1].xpath("span/style/text()")
                ip_dn_classes = re.findall("\.([^\{]+)\{display:\s*none\}", raw_ip_style_text[0])
                for ip_dn_class in ip_dn_classes:
                    ip_dn_class_divs = re.findall('<div\s*class="' + ip_dn_class + '">\d*</div>', raw_ip)
                    for ip_dn_class_div in ip_dn_class_divs:
                        raw_ip = raw_ip.replace(ip_dn_class_div, '')
                    ip_dn_class_spans = re.findall('<span\s*class="' + ip_dn_class + '">\d*</span>', raw_ip)
                    for ip_dn_class_span in ip_dn_class_spans:
                        raw_ip = raw_ip.replace(ip_dn_class_span, '')
                ip_dn_divs = re.findall('<div\s*style="display:\s*none">\d*</div>', raw_ip)
                for ip_dn_div in ip_dn_divs:
                    raw_ip = raw_ip.replace(ip_dn_div, '')
                ip_dn_spans = re.findall('<span\s*style="display:\s*none">\d*</span>', raw_ip)
                for ip_dn_span in ip_dn_spans:
                    raw_ip = raw_ip.replace(ip_dn_span, '')
                ip_parts = re.findall('>\s*([\.0-9]+)\s*<', raw_ip)
                fp = orm.FreeProxy()
                fp.ip = ''.join(ip_parts)
                fp.port = raw_proxy[2].text.strip()
                fp.protocol = raw_proxy[6].text.lower().strip()
                if fp.protocol in ('socks4/5', 'https', 'http'):
                    try:
                        ses.query(orm.FreeProxy).filter(orm.and_(orm.and_(orm.FreeProxy.ip == fp.ip, orm.FreeProxy.port == fp.port),
                            orm.FreeProxy.protocol == fp.protocol)).one()
                    except orm.NoResultFound:
                        ses.add(fp)
                        ses.commit()
                        added_fps.append((fp.ip, fp.port, fp.protocol))
            except:
                froxly_grabber_log.exception(traceback.format_exc() + '\n\n' + etree.tostring(raw_proxy).decode('utf-8'))
                end_time = time.time()
                exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
                froxly_grabber_log.info('Finished, duration is %s \n\n' % (str(exec_delta),))
        ses.close()
        conn.close()
        report = str(len(added_fps)) + ' new proxies were added'
        for added_fp in added_fps:
            report += '\n' + str(added_fp)
        froxly_grabber_log.info(report)
        end_time = time.time()
        exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
        froxly_grabber_log.info('Finished, duration is %s \n\n' % (str(exec_delta),))
    except:
        froxly_grabber_log.fatal(traceback.format_exc() + '\n\n' + str(res_data))
        end_time = time.time()
        exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
        froxly_grabber_log.info('Finished, duration is %s \n\n' % (str(exec_delta),))
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()
else:
    froxly_grabber_log.info('Grabber already started')
import urllib.request
import urllib.parse
from lxml import etree
import datetime
import time
import io
import re
import random
import traceback
import zmq
import json
import redis

from werp import orm
from werp import nlog
from werp.common import sockets
from werp.common import timeouts
from werp.common import red_keys

TRY_COUNT = 11
url = 'http://www.hidemyass.com/proxy-list/'
conn = None
ses = None
ctx = None
try:
    start_dt = datetime.datetime.now()
    start_time = time.time()
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    res = None
    res_data = None
    try_count = 0
    ctx = zmq.Context()
    rnd_user_agent_socket = ctx.socket(zmq.REQ)
    rnd_user_agent_socket.connect(sockets.rnd_user_agent)
    froxly_data_server_socket = ctx.socket(zmq.REQ)
    froxly_data_server_socket.connect(sockets.froxly_data_server)
    while res is None and try_count < TRY_COUNT:
        rnd_proxy = None
        froxly_data_server_socket.send_unicode(json.dumps({'method': 'rnd', 'params': None}))
        rnd_proxy_res = json.loads(froxly_data_server_socket.recv_unicode())
        if rnd_proxy_res is not None:
            rnd_proxy = rnd_proxy_res['result']        
        rnd_user_agent_socket.send_unicode('')
        rnd_user_agent = rnd_user_agent_socket.recv_unicode()
        try:
            s = socket.socket()
            s.settimeout(timeouts.froxly_grabber)
            url_obj = urllib.parse.urlparse(url)
            s.connect((rnd_proxy['ip'], int(rnd_proxy['port'])))
            req_str = 'GET ' + url + ' HTTP/1.1\r\nHost:' + url_obj.netloc + '\r\n\r\n'
            
            nlog.info('froxly - grabber info', req_str)
            
            s.sendall(req_str.encode())
            res = s.recv(15).decode()
            
            nlog.info('froxly - grabber info', res)
            
            if res == 'HTTP/1.1 200 OK' or res == 'HTTP/1.0 200 OK':
                buf = s.recv(1024)
                while buf:
                    res += buf.decode()
                    buf = s.recv(1024)
                start_body = res.find('\r\n\r\n')
                res_data = res[start_body + 4:]
                res = None
            s.close()
            nlog.info('froxly - grabber info', res_data)
        except:
            
            nlog.info('froxly - grabber info', traceback.format_exc())
            
            res = None
        try_count = try_count + 1
        if try_count >= TRY_COUNT:
            nlog.info('froxly - grabber error - request data', str(TRY_COUNT) + ' tries have failed.')
    html_parser = etree.HTMLParser()
    dom_tree = etree.parse(io.StringIO(res_data), html_parser)
    raw_proxies = dom_tree.xpath('/html/body/div/div/table/tr')
    for raw_proxy in raw_proxies:
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
        try:
            ses.query(orm.FreeProxy).filter(orm.and_(orm.and_(orm.FreeProxy.ip == fp.ip, orm.FreeProxy.port == fp.port),
                orm.FreeProxy.protocol == fp.protocol)).one()
        except orm.NoResultFound:
            ses.add(fp)
            ses.commit()
    ses.close()
    conn.close()
    end_time = time.time()
    exec_delta = datetime.timedelta(seconds=int(end_time - start_time))
    red = redis.StrictRedis(unix_socket_path=sockets.redis)
    red.rpush(red_keys.exec_time_log, 'froxly grabber %s %s' % (str(start_dt), str(exec_delta)))
except:
    nlog.info('froxly - grabber error', traceback.format_exc())
    if ses is not None:
        ses.close()
    if conn is not None:    
        conn.close()
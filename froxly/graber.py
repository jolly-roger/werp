import urllib.request
import urllib.parse
from lxml import etree
import io
import re
import random
import smtplib
from email.mime.text import MIMEText
import traceback

from werp import orm

url = 'http://www.hidemyass.com/proxy-list/'

try:
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    res = None
    try_count = 0
    while res is None and try_count < 11:
        proxies = ses.query(orm.FreeProxy).filter(orm.FreeProxy.protocol == 'http').all()
        user_agents = ses.query(orm.UserAgent).filter(orm.UserAgent.is_bot == False).all()
        rnd_proxy = random.choice(proxies)
        rnd_user_agent = random.choice(user_agents)
        req = urllib.request.Request(url, headers={'User-Agent': rnd_user_agent.value})
        req.set_proxy(rnd_proxy.ip + ':' + rnd_proxy.port, rnd_proxy.protocol)
        res = urllib.request.urlopen(req)
        print(str(res.getcode()))
        if res.getcode() != 200:
            print('Fuck!!!')
            res = None
        try_count = try_count + 1
    html_parser = etree.HTMLParser()
    res_data = res.read().decode('utf-8')
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
                orm.FreeProxy.protocol == fp.protocot)).one()
        except orm.NoResultFound:
            ses.add(fp)
            ses.commit()
    ses.close()
    conn.close()
except:
    sender = 'www@dig-dns.com (www)'
    recipient = 'roger@dig-dns.com'

    msg = MIMEText(traceback.format_exc())
    msg['Subject'] = 'req_logger - parse log error'
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()






    
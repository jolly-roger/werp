from lxml import etree
import urllib.parse
import html
import html.parser
import os.path
import io

from . import getenv
from werp import orm

TEMPLATES_DIR = '/home/www/ukrainianside/layout/templates'

def getAll():
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    rawAliases = ses.query(orm.ukrainianside.Article).order_by(orm.desc(orm.ukrainianside.Article.order)).all()
    ses.close()
    conn.close()
    return rawAliases
def getUrlByAlias(alias):
    articles = getAll()
    for a in articles:
        if a.alias == alias:
            return 'http://ukrainianside.com/' + a.title.strip().replace(' ', '+')
    return ''
def getAliasUrlByAlias(alias):
    return 'http://ukrainianside.com/' + alias.strip().replace(' ', '+')
def getQuotedUrlByAlias(alias):
    articles = getAll()
    for a in articles:
        if a.alias == alias:
            return urllib.parse.quote('http://ukrainianside.com/' + a.title.strip().replace(' ', '+'))
    return ''
def getTitleByAlias(alias):
    articles = getAll()
    for a in articles:
        if a.alias == alias:
            return a.title
    return ''
def getAliasByTitle(title):
    articles = getAll()
    for a in articles:
        if a.title.lower().strip() == title.lower().strip():
            return a.alias
    return ''
def getArticleDescByAlias(alias):
    desc = ''
    if os.path.exists(TEMPLATES_DIR + '/pages/' + alias + '.html'):
        parser = etree.HTMLParser()
        tree = etree.parse(io.StringIO(open(TEMPLATES_DIR + '/pages/' + alias + '.html').read()), parser)
        raw_desc = tree.xpath('//article/p[1]')
        if len(raw_desc) > 0:
            desc = getenv().\
                from_string(html.parser.HTMLParser().unescape(etree.tostring(raw_desc[0]).decode('utf8'))).render()
    return desc
def getArticleEscapedDescByAlias(alias):
    return html.escape(getArticleDescByAlias(alias))
def getAticlesSeq():
    articles = getAll()
    ordered_aliases = []
    for a in articles:
        ordered_aliases.append(a.alias)
    return ordered_aliases
def getArticleMainImageUrl(alias):
    if os.path.exists(TEMPLATES_DIR + '/images/' + alias) and \
        os.path.exists(TEMPLATES_DIR + '/images/' + alias + '/main.jpg'):
            return 'http://ukrainianside.com/images/' + alias + '/main.jpg'
    else:
        return 'http://ukrainianside.com/images/logo.jpg'

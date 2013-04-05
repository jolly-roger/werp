import datetime
import cherrypy
import traceback

from . import orm
from . import notifier
from .common import etype

def getSitemap(lng):    
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>' +\
        '<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +\
            'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 ' +\
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" ' +\
            'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +\
            '<url>' +\
                '<loc>' + cherrypy.request.base + '</loc>' +\
                '<lastmod>' + now + '</lastmod>' +\
                '<changefreq>daily</changefreq>' +\
                '<priority>1.0</priority>' +\
            '</url>' +\
            '<url>' +\
                '<loc>' + cherrypy.request.base + '/news</loc>' +\
                '<lastmod>' + now + '</lastmod>' +\
                '<changefreq>daily</changefreq>' +\
                '<priority>1.0</priority>' +\
            '</url>' +\
            '<url>' +\
                '<loc>' + cherrypy.request.base + '/ss</loc>' +\
                '<lastmod>' + now + '</lastmod>' +\
                '<changefreq>daily</changefreq>' +\
                '<priority>1.0</priority>' +\
            '</url>' +\
            '<url>' +\
                '<loc>' + cherrypy.request.base + '/ts</loc>' +\
                '<lastmod>' + now + '</lastmod>' +\
                '<changefreq>daily</changefreq>' +\
                '<priority>1.0</priority>' +\
            '</url>' +\
        '</urlset>'
    return sitemap
def getTrainSitemap(lng):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    ts = None
    try:
        ts = ses.query(orm.E).filter(orm.E.etype == etype.train).all()
    except:
        notifier.notify('Uatrains error', 'Can\'t create sitemap\n' + traceback.format_exc())
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>' +\
        '<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +\
            'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 ' +\
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" ' +\
            'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    if ts is not None:
        for t in ts:
            sitemap += '<url>' +\
                    '<loc>' + cherrypy.request.base + '/' + str(t.id) + '</loc>' +\
                    '<lastmod>' + now + '</lastmod>' +\
                    '<changefreq>daily</changefreq>' +\
                    '<priority>1.0</priority>' +\
                '</url>'
    sitemap += '</urlset>'
    return sitemap
def getStationSitemap(lng):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    ss = None
    try:
        ss = ses.query(orm.E).filter(orm.E.etype == etype.station).all()
    except:
        notifier.notify('Uatrains error', 'Can\'t create sitemap\n' + traceback.format_exc())
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>' +\
        '<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +\
            'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 ' +\
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" ' +\
            'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    if ss is not None:
        for s in ss:
            sitemap += '<url>' +\
                    '<loc>' + cherrypy.request.base + '/' + str(s.id) + '</loc>' +\
                    '<lastmod>' + now + '</lastmod>' +\
                    '<changefreq>daily</changefreq>' +\
                    '<priority>1.0</priority>' +\
                '</url>'
    sitemap += '</urlset>'
    return sitemap
def getPTrainSitemap(lng):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    pts = None
    try:
        pts = ses.query(orm.E).filter(orm.E.etype == etype.ptrain).all()
    except:
        notifier.notify('Uatrains error', 'Can\'t create sitemap\n' + traceback.format_exc())
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>' +\
        '<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +\
            'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 ' +\
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" ' +\
            'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    if pts is not None:
        for pt in pts:
            sitemap += '<url>' +\
                    '<loc>' + cherrypy.request.base + '/' + str(pt.id) + '</loc>' +\
                    '<lastmod>' + now + '</lastmod>' +\
                    '<changefreq>daily</changefreq>' +\
                    '<priority>1.0</priority>' +\
                '</url>'
    sitemap += '</urlset>'
    return sitemap
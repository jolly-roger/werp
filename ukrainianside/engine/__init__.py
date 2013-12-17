from jinja2 import Environment, FileSystemLoader
import urllib.request
import urllib.parse

env = None

def getenv():
    global env
    
    if env is None:
        env = Environment(loader = FileSystemLoader("/home/www/ukrainianside/layout/templates"))
    return env

def getRailwayTimetable(rwid):
    raw_rwtt = urllib.request.urlopen('http://localhost:18050/get_railway_timetable/' + str(rwid))
    return raw_rwtt.read().decode('utf-8')

from . import article

getenv().globals["continueReading"] = "Читать далее "
getenv().globals["getUrlByAlias"] = article.getUrlByAlias
getenv().globals["getAliasUrlByAlias"] = article.getAliasUrlByAlias
getenv().globals["getQuotedUrlByAlias"] = article.getQuotedUrlByAlias
getenv().globals["getTitleByAlias"] = article.getTitleByAlias
getenv().globals["getArticleDescByAlias"] = article.getArticleDescByAlias
getenv().globals["getArticleEscapedDescByAlias"] = article.getArticleEscapedDescByAlias
getenv().globals["getArticleMainImageUrl"] = article.getArticleMainImageUrl
getenv().globals["getAticlesSeq"] = article.getAticlesSeq
getenv().globals['getRailwayTimetable'] = getRailwayTimetable
getenv().globals['quote'] = urllib.parse.quote
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
getenv().globals["getUrlByAlias"] = getUrlByAlias
getenv().globals["getAliasUrlByAlias"] = getAliasUrlByAlias
getenv().globals["getQuotedUrlByAlias"] = getQuotedUrlByAlias
getenv().globals["getTitleByAlias"] = getTitleByAlias
getenv().globals["getArticleDescByAlias"] = getArticleDescByAlias
getenv().globals["getArticleEscapedDescByAlias"] = getArticleEscapedDescByAlias
getenv().globals["getArticleMainImageUrl"] = getArticleMainImageUrl
getenv().globals["getAticlesSeq"] = getAticlesSeq
getenv().globals['getRailwayTimetable'] = getRailwayTimetable
getenv().globals['quote'] = urllib.parse.quote
import cherrypy
import random
import urllib.request
import urllib.parse
from jinja2 import Environment, FileSystemLoader

from .. import engine

env = None

def getenv():
    global env
    
    if env is None:
        env = Environment(loader = FileSystemLoader("/home/www/ukrainianside/layout/templates"))
        env.globals["continueReading"] = "Читать далее "
        env.globals["getUrlByAlias"] = engine.article.getUrlByAlias
        env.globals["getAliasUrlByAlias"] = engine.article.getAliasUrlByAlias
        env.globals["getQuotedUrlByAlias"] = engine.article.getQuotedUrlByAlias
        env.globals["getTitleByAlias"] = engine.article.getTitleByAlias
        env.globals["getArticleDescByAlias"] = engine.article.getArticleDescByAlias
        env.globals["getArticleEscapedDescByAlias"] = engine.article.getArticleEscapedDescByAlias
        env.globals["getArticleMainImageUrl"] = engine.article.getArticleMainImageUrl
        env.globals["getAticlesSeq"] = engine.article.getAticlesSeq
        env.globals['getRailwayTimetable'] = getRailwayTimetable
        env.globals['quote'] = urllib.parse.quote
    return env

def getCategory(categoryName):
    tmpl = getenv().get_template("pages/" + categoryName + ".html")
    return tmpl.render()

def getAticle(articleTitle, aticleName):
    tmpl = getenv().get_template("pages/" + aticleName + ".html")
    return tmpl.render(articleTitle=articleTitle, articleAlias=aticleName)

def getIndex():
    return getHome()
    
def getHome():
    tmpl = getenv().get_template("pages/home.html")
    return tmpl.render()

def getCss():
    tmpl = getenv().get_template("css/style.css")
    return tmpl.render()


def getRailwayTimetable(rwid):
    raw_rwtt = urllib.request.urlopen('http://localhost:18050/get_railway_timetable/' + str(rwid))
    return raw_rwtt.read().decode('utf-8')
    
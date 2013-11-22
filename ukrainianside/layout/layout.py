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
        env.globals["getNameByAlias"] = engine.article.getNameByAlias
        env.globals["getAticleDescByAlias"] = engine.article.getAticleDescByAlias
        env.globals["getAticlesSeq"] = engine.article.getAticlesSeq
        env.globals['getRailwayTimetable'] = getRailwayTimetable
    return env

def getCategory(categoryName):
    tmpl = getenv().get_template("pages/" + categoryName + ".html")
    return tmpl.render()

def getAticle(aticleName):
    tmpl = getenv().get_template("pages/" + aticleName + ".html")
    return tmpl.render()

def getIndex():
    return getHome()
    
def getHome():
    tmpl = getenv().get_template("pages/home.html")
    return tmpl.render()

def getCss(lng='EN'):
    tmpl = getenv().get_template("css/style.css")
    return tmpl.render()


def getRailwayTimetable(rwid):
    raw_rwtt = urllib.request.urlopen('http://localhost:18050/get_railway_timetable/' + str(rwid))
    return raw_rwtt.read().decode('utf-8')
    
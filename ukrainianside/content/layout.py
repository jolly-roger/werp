import cherrypy
import random
import urllib.request
import urllib.parse
from jinja2 import Environment, FileSystemLoader

from .. import data


env = None


def getenv():
    global env
    
    if env is None:
        env = Environment(loader = FileSystemLoader("/home/www/ukrainianside/" + \
            "content"))
        env.globals["postedIn"] = "Опубликована в "
        env.globals["continueReading"] = "Читать далее "
        env.globals["getUrlByAlias"] = data.urls.getUrlByAlias
        env.globals["getNameByAlias"] = data.names.getNameByAlias
        env.globals["randint"] = random.randint
        env.globals["getAticleDescByAlias"] = data.descs.getAticleDescByAlias
        env.globals["getCategoryAliasByAticleAlias"] = data.categories.getCategoryAliasByAticleAlias
        env.globals["getAticlesSeq"] = data.seq.getAticlesSeq
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


def getRailwayTimetable(rwid):
    raw_rwtt = urllib.request.urlopen('http://localhost:18050/get_railway_timetable/' + str(rwid))
    return raw_rwtt.read().decode('utf-8')
    
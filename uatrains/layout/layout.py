import cherrypy
from jinja2 import Environment, FileSystemLoader
import gettext
import configparser

from ..engine import lng as lngs

config = configparser.ConfigParser()
config.read('/home/www/uatrains/app.conf')

def getenv(lng=lngs.UA):
    if lng == lngs.UA:
        return ua_env
    elif lng == lngs.RU:
        return ru_env
    elif lng == lngs.EN:
        return en_env
    return ua_env

def getCss():
    tmpl = getenv().get_template("css/style.css")
    return tmpl.render()

def get_lng_title(e, lng):
    if lng == lngs.RU:
        return e.ru_title
    elif lng == lngs.EN:
        return e.en_title
    return e.ua_title
def get_lng_period(e, lng):
    if lng == lngs.RU:
        return e.ru_period
    elif lng == lngs.EN:
        return e.en_period
    return e.ua_period
def get_search_lng_title(e, ph, lng):
    in_ua = None
    in_ru = None
    in_en = None
    if e.ua_title is not None:
        in_ua = ph.lower() in e.ua_title.lower()
    if e.ru_title is not None:
        in_ru = ph.lower() in e.ru_title.lower()
    if e.en_title is not None:
        in_en = ph.lower() in e.en_title.lower()
    if lng == lngs.UA:
        if in_ua:
            return (lngs.UA, e.ua_title)
        elif in_ru:
            return (lngs.RU, e.ru_title)
        elif in_en:
            return (lngs.EN, e.en_title)
    elif lng == lngs.RU:
        if in_ru:
            return (lngs.RU, e.ru_title)
        elif in_ua:
            return (lngs.UA, e.ua_title)
        elif in_en:
            return (lngs.EN, e.en_title)
    elif lng == lngs.EN:
        if in_en:
            return (lngs.EN, e.en_title)
        elif in_ua:
            return (lngs.UA, e.ua_title)
        elif in_ru:
            return (lngs.RU, e.ru_title)
    return (lngs.UA, e.ua_title)

def getHome(ts, ss, news, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/home.html")
    return tmpl.render(ts=ts, ss=ss, news=news, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)
def getTrain(train, train_stations, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/train.html")
    return tmpl.render(train=train, train_stations=train_stations, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)
def getPTrain(train, train_stations, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/ptrain.html")
    return tmpl.render(train=train, train_stations=train_stations, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)
def getTrains(ts, phrase, pn, has_next_p, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/trains.html")
    return tmpl.render(trains=ts, phrase=phrase, pn=pn, has_next_p=has_next_p, is_trains=True, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)
def getStation(station, station_trains, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/station.html")
    return tmpl.render(station=station, station_trains=station_trains, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)
def getStations(stations, ph, pn, has_next_p, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/stations.html")
    return tmpl.render(stations=stations, ph=ph, pn=pn, has_next_p=has_next_p, is_stations=True, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)
def getEs(es, srcht, ph, fs, ts, pn, has_next_p, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/es.html")
    return tmpl.render(es=es, srcht=srcht, ph=ph, fs=fs, ts=ts, pn=pn, has_next_p=has_next_p, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)
def getNews(news, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/news.html")
    return tmpl.render(news=news, is_news=True, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)
def getRailwayTimetable(railway, lng=lngs.UA):
    tmpl = getenv(lng).get_template("pages/railwaytimetable.html")
    return tmpl.render(railway=railway, lng=lng,
        path_info=cherrypy.request.path_info, query_string=cherrypy.request.query_string)

trans_ru_RU = gettext.translation('messages', languages=['ru_RU'], localedir=config['global']['layout.trans'])
trans_uk_UA = gettext.translation('messages', languages=['uk_UA'], localedir=config['global']['layout.trans'])
trans_en_US = gettext.translation('messages', languages=['en_US'], localedir=config['global']['layout.trans'])

ua_env = Environment(loader = FileSystemLoader(config['global']['layout.templates']), extensions=['jinja2.ext.i18n'])
ua_env.install_gettext_translations(trans_uk_UA)
ua_env.globals['get_lng_title'] = get_lng_title
ua_env.globals['get_lng_period'] = get_lng_period
ua_env.globals['get_search_lng_title'] = get_search_lng_title
ua_env.globals['ua_domain'] = config['global']['domains.ua']
ua_env.globals['ru_domain'] = config['global']['domains.ru']
ua_env.globals['en_domain'] = config['global']['domains.en']
ru_env = Environment(loader = FileSystemLoader(config['global']['layout.templates']), extensions=['jinja2.ext.i18n'])
ru_env.install_gettext_translations(trans_ru_RU)
ru_env.globals['get_lng_title'] = get_lng_title
ru_env.globals['get_lng_period'] = get_lng_period
ru_env.globals['get_search_lng_title'] = get_search_lng_title
ru_env.globals['ua_domain'] = config['global']['domains.ua']
ru_env.globals['ru_domain'] = config['global']['domains.ru']
ru_env.globals['en_domain'] = config['global']['domains.en']
en_env = Environment(loader = FileSystemLoader(config['global']['layout.templates']), extensions=['jinja2.ext.i18n'])
en_env.install_gettext_translations(trans_en_US)
en_env.globals['get_lng_title'] = get_lng_title
en_env.globals['get_lng_period'] = get_lng_period
en_env.globals['get_search_lng_title'] = get_search_lng_title
en_env.globals['ua_domain'] = config['global']['domains.ua']
en_env.globals['ru_domain'] = config['global']['domains.ru']
en_env.globals['en_domain'] = config['global']['domains.en']
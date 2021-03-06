import cherrypy
from jinja2 import Environment, FileSystemLoader
import gettext
import configparser

config = configparser.ConfigParser()
config.read('/home/www/dap/app.conf')

def getenv(lng='EN'):
    if lng == 'RU':
        return ru_env
    return en_env

def getCss(lng='EN'):
    tmpl = getenv(lng).get_template("css/style.css")
    return tmpl.render()

def getJS(page, lng='EN'):
    tmpl = getenv(lng).get_template("js/script.js")
    return tmpl.render(page=page)

def getHome(lng='EN'):
    tmpl = getenv(lng).get_template("pages/home.html")
    return tmpl.render(lng=lng)

def getCheck(domain, ses_key, proxies, jproxies, lng='EN'):
    tmpl = getenv(lng).get_template("pages/check.html")
    return tmpl.render(domain=domain, ses_key=ses_key, proxies=proxies, jproxies=jproxies, lng=lng)

trans_ru_RU = gettext.translation('messages', languages=['ru_RU'], localedir=config['global']['layout.trans'])
trans_en_US = gettext.translation('messages', languages=['en_US'], localedir=config['global']['layout.trans'])

ru_env = Environment(loader = FileSystemLoader(config['global']['layout.templates']), extensions=['jinja2.ext.i18n'])
ru_env.install_gettext_translations(trans_ru_RU)
ru_env.globals['ru_domain'] = config['global']['domains.ru']
ru_env.globals['en_domain'] = config['global']['domains.en']
en_env = Environment(loader = FileSystemLoader(config['global']['layout.templates']), extensions=['jinja2.ext.i18n'])
en_env.install_gettext_translations(trans_en_US)
en_env.globals['ru_domain'] = config['global']['domains.ru']
en_env.globals['en_domain'] = config['global']['domains.en']
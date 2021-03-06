import cherrypy
from jinja2 import Environment, FileSystemLoader
import gettext
import configparser

config = configparser.ConfigParser()
config.read('/home/www/ugently/app.conf')

def getenv(lng='RU'):
    if lng == 'RU':
        return ru_env
    return en_env

def getHome(user_agents, lng='EN'):
    tmpl = getenv(lng).get_template("pages/home.html")
    return tmpl.render(user_agents=user_agents)

def getLogin(name, pwd, lng='EN'):
    tmpl = getenv(lng).get_template("pages/login.html")
    return tmpl.render()

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
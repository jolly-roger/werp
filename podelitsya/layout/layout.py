from jinja2 import Environment, FileSystemLoader

env = None

def getenv():
    global env    
    if env is None:
        env = Environment(loader = FileSystemLoader("/home/www/podelitsya/layout/templates"))
    return env

def getSocial(quoted_url, title):
    tmpl = getenv().get_template("pages/social.html")
    return tmpl.render(quoted_url=quoted_url, title=title)

def getCss():
    tmpl = getenv().get_template("css/style.css")
    return tmpl.render()
    
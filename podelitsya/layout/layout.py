from jinja2 import Environment, FileSystemLoader

env = None

def getenv():
    global env    
    if env is None:
        env = Environment(loader = FileSystemLoader("/home/www/podelitsya/layout/templates"))
    return env

def getHome():
    tmpl = getenv().get_template("pages/home.html")
    return tmpl.render()

def getSocial(quoted_url, title, display_label, is_vertical):
    tmpl = getenv().get_template("pages/social.html")
    return tmpl.render(quoted_url=quoted_url, title=title, display_label=display_label, is_vertical=is_vertical)

def getSocialCss():
    tmpl = getenv().get_template("css/social.css")
    return tmpl.render()

def getCss():
    tmpl = getenv().get_template("css/style.css")
    return tmpl.render()
    
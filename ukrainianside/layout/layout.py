from .. import engine

def getCategory(categoryName):
    tmpl = engine.getenv().get_template("pages/" + categoryName + ".html")
    return tmpl.render()

def getAticle(articleTitle, aticleName):
    tmpl = engine.getenv().get_template("pages/" + aticleName + ".html")
    return tmpl.render(articleTitle=articleTitle, articleAlias=aticleName)

def getIndex():
    return getHome()
    
def getHome():
    tmpl = engine.getenv().get_template("pages/home.html")
    return tmpl.render()

def getCss():
    tmpl = engine.getenv().get_template("css/style.css")
    return tmpl.render()
    
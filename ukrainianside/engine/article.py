from werp import orm

def getAll():
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    rawAliases = ses.query(orm.ukrainianside.Article).order_by(orm.desc(orm.ukrainianside.Article.order)).all()
    ses.close()
    conn.close()
    return rawAliases
def isExist(alias, articles = None):
    if articles is None:
        articles = getAll()
    for a in articles:
        if a.alias == alias:
            return True
    return False
def getUrlByAlias(alias):
    articles = getAll()
    for a in articles:
        if a.alias == alias:
            return 'http://ukrainianside.com/' + a.title
    return ''
def getTitleByAlias(alias):
    articles = getAll()
    for a in articles:
        if a.alias == alias:
            return a.title
    return ''
def getAliasByTitle(title):
    articles = getAll()
    for a in articles:
        if a.title.lower().trim() == title.lower().trim():
            return a.alias
    return ''
def getAticleDescByAlias(alias):
    articles = getAll()
    for a in articles:
        if a.alias == alias:
            return a.description
    return ''
def getAticlesSeq():
    articles = getAll()
    ordered_aliases = []
    for a in articles:
        ordered_aliases.append(a.alias)
    return ordered_aliases
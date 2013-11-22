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
            return a.url
    return ''
def getNameByAlias(alias):
    articles = getAll()
    for a in articles:
        if a.alias == alias:
            return a.name
    return ''
def getAticleDescByAlias(alias):
    articles = getAll()
    for a in articles:
        if a.alias == alias:
            return a.order
    return 0
def getAticlesSeq():
    articles = getAll()
    ordered_aliases = []
    for a in articles:
        ordered_aliases.append(a.alias)
    return ordered_aliases
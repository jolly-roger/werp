from werp import orm

def getAll():
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    rawAliases = ses.query(orm.ukrainianside.Article).all()
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
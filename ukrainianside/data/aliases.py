import sqlite3
import cherrypy


def getAll():
    conn = sqlite3.connect("/home/www/ukrainianside/" + "data/data.db")
    cur = conn.cursor()
        
    cur.execute("select value from aliases;")
    rawAliases = cur.fetchall()
        
    cur.close()
    conn.close()
    
    return rawAliases

def isExist(alias, aliases = None):
    if aliases is None:
        aliases = getAll()
    
    for al in aliases:
        if al[0] == alias:
            return True
        
    return False
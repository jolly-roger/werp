import sqlite3
import cherrypy


def getNameByAlias(alias):
    conn = sqlite3.connect("/home/www/ukrainianside/" + "data/data.db")
    cur = conn.cursor()
        
    cur.execute("select n.value from aliases as a, names as n, relation as r "\
        "where a.id = r.alias_id and n.id = r.name_id and a.value = ?;", (alias, ))
    rawName = cur.fetchone()
        
    cur.close()
    conn.close()
    
    return rawName[0]
import sqlite3
import cherrypy


def getAticlesSeq():
    conn = sqlite3.connect("/home/www/ukrainianside/" + "data/data.db")
    cur = conn.cursor()
        
    cur.execute("select al.value from aliases as al, aticles as at, seq "\
        "where al.id = at.alias_id and at.id = seq.aticle_id order by seq.value desc;")
    rawAticlesSeq = cur.fetchall()
        
    cur.close()
    conn.close()
    
    aliases = []
    
    for rawAlias in rawAticlesSeq:
        aliases.append(rawAlias[0])
    
    return aliases
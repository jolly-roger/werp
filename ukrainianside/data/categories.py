import sqlite3
import cherrypy


def getCategoryAliasByAticleAlias(alias):
    conn = sqlite3.connect("/home/www/ukrainianside/" + "data/data.db")
    cur = conn.cursor()

    cur.execute("select al1.value from aliases as al0, aliases as al1, aticles as at, categories as c, " + \
        "category_aticle as ca "\
        "where al0.id = at.alias_id and at.id = ca.aticle_id and ca.category_id = c.id and c.alias_id = al1.id " + \
        "and al0.value = ?;", (alias, ))
    rawAlias = cur.fetchone()

    cur.close()
    conn.close()
    
    return rawAlias[0]
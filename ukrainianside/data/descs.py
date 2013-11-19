import sqlite3
import cherrypy


def getAticleDescByAlias(alias):
	conn = sqlite3.connect("/home/www/ukrainianside/" + "data/data.db")
	cur = conn.cursor()
	
	cur.execute("select d.value from aliases as al, descs as d, aticles as at "\
		"where al.id = at.alias_id and at.desc_id = d.id and al.value = ?;", (alias, ))
	rawDesc = cur.fetchone()
	
	cur.close()
	conn.close()
	
	return rawDesc[0]
	
from werp import orm
from werp.uatrains import bot

def add_history(ses, e, htype):    
    try:
        he = orm.uatrains.he.from_e(e, htype)
        ses.add(he)
        ses.commit()
    except:
        bot.logger.error('Can\'t write history for e with id: ' + str(e.id) + '\r\n')
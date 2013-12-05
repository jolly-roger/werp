from . import odessa
from . import southwest
from . import passengers

from . import common

from werp import orm
from werp.uatrains import bot
from werp.uatrains.engine import triggers

def get_train_data(drv_module, tid, ua_dom_tree):
    ses = None
    conn = None
    try:
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        e = drv_module.from_remote(ua_dom_tree, tid)
        if e is not None:
            if common.is_not_empty(e):
                t = common.get_t(e, ses)
                if t is None:
                    if common.e_has_all_data(e):
                        ses.add(e)
                        ses.commit()
                        t = e
                        triggers.e.add_history(ses, t, orm.uatrains.htype.insert)
                    else:
                        bot.logger.error('Train has no all data\r\ntid: ' + str(tid) + '\r\n' +\
                            'ua_title: ' + str(e.ua_title) + '\r\n' +\
                            'value: ' + str(e.value) + '\r\n' +\
                            'oid: ' + str(e.oid) + '\r\n')
                        raise Exception(drv_module.name + ' driver train entity has empty fields')
                else:
                    if t.ua_title is None:
                        t.ua_title = e.ua_title
                    if e.ua_period is not None:
                        t.ua_period = e.ua_period
                    if e.from_date is not None:
                        t.from_date = e.from_date
                    if e.to_date is not None:
                        t.to_date = e.to_date
                    ses.commit()
                    triggers.e.add_history(ses, t, orm.uatrains.htype.update)
                drv_module.link_to_station(ua_dom_tree, t, ses)
        ses.commit()
        ses.close()
        conn.close()
    except Exception as e:
        if ses is not None:
            ses.close()
        if conn is not None:
            conn.close()
        raise e
def check_dom_tree(current_drv, dom_tree):
    if len(dom_tree.xpath(current_drv.xtattrs)) <= 0: raise Exception('Train dom attributes are empty')
    if len(dom_tree.xpath(current_drv.xttitle)) <= 0: raise Exception('Train dom title is empty')
    if len(dom_tree.xpath(current_drv.xtvalue)) <= 0: raise Exception('Train dom value is empty')
    if len(dom_tree.xpath(current_drv.xtperiod)) <= 0: raise Exception('Train dom period is empty')
    if len(dom_tree.xpath(current_drv.xts)) <= 0: raise Exception('Train dom stations are empty')
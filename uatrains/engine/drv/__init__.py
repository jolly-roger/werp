from . import odessa
from . import southwest
from . import passengers

from . import common
from ... import orm

from werp.uatrains import bot

def get_train_data(drv_module, tid, ua_dom_tree, ru_dom_tree, en_dom_tree):
    ses = None
    conn = None
    try:
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        e = drv_module.from_remote(ua_dom_tree, ru_dom_tree, en_dom_tree, tid)
        if e is not None:
            if common.is_not_empty(e):
                t = common.get_t(e, ses)
                if t is None:
                    if common.has_all_data(e):
                        ses.add(e)
                        t = e
                    else:
                        bot.logger.error('Train has no all data\r\ntid: ' + str(tid))
                        raise Exception(drv_module.name + ' driver train entity has empty fields')
                else:
                    if t.ua_title is None:
                        t.ua_title = e.ua_title
                    if t.ru_title is None:
                        t.ru_title = e.ru_title
                    if t.en_title is None:
                        t.en_title = e.en_title
                    if e.ua_period is not None:
                        t.ua_period = e.ua_period
                    if e.ru_period is not None:
                        t.ru_period = e.ru_period
                    if e.en_period is not None:
                        t.en_period = e.en_period
                ses.commit()
                drv_module.link_to_station(ua_dom_tree, ru_dom_tree, en_dom_tree, t, ses)
        ses.commit()
        ses.close()
        conn.close()
    except Exception as e:
        if ses is not None:
            ses.close()
        if conn is not None:
            conn.close()
        raise e
from .. import orm
from . import srctype
from . import dstype

pn_tid = 'tid'
pn_sid = 'sid'
pn_rid = 'rid'
pn_lng = 'lng'

def get_data_srcs(ses):
    return ses.query(orm.Src).\
        options(orm.joinedload_all(orm.Src.dspathes)).\
        filter(orm.Src.type == srctype.data).all()
def get_dspath(src, dst):
    for dspath in src.dspathes:
        if dspath.dstype == dst:
            return dspath
    return None
def has_t_dspathes(ds):
    if get_dspath(ds, dstype.ttitle) is not None and get_dspath(ds, dstype.tvalue) is not None and\
        get_dspath(ds, dstype.tperiod) is not None:
        return True
    return False
#def has_s_dspathes(ds):
#    if get_dspath(ds, dstype.stitle) is not None:
#        return True
#    return False
#def get_geo_srcs(ses):
#    return ses.query(orm.Src).filter(orm.Src.type == srctype.geo).all()
#def get_train_url(src, params):
#    return src.url.replace('(tid)', str(params[0])).replace('(lng)', params[1])
#def get_station_url(src, params):
#    url_tmp = src.url + '?' + pn_sid + '=%s&' + pn_lng + '=%s'
#    return url_tmp % params
#def get_route_url(src, params):
#    url_tmp = src.url + '?' + pn_rid + '=%s&' + pn_lng + '=%s'
#    return url_tmp % params
#def get_geo_url(src, params):
#    url_tmp = src.url + '&' + pn_lng + '=%s'
#    return url_tmp % params
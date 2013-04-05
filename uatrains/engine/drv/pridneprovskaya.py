#import urllib.request
#from lxml import etree
#
#
#def get_train_data():
#    data_map = urllib.request.urlopen(src.get_train_url(data_src, (tid, lngs[lng])))
#    res_data = res.read().decode('cp1251')
#    
#def get_station_data():
#    data_map_res = urllib.request.urlopen('http://www.dp.uz.gov.ua/timetable/')
#    data_map = data_map_res.read().decode('cp1251')
#    parser = etree.HTMLParser()
#    dom_tree = etree.parse(io.StringIO(data_map), parser)
#    raw_station_map = dom_tree.xpath('/html/body/div/div[3]/div/div/div/div[4]/form/select/option')
#    #for rsm in raw_station_map:
#        
#    
import cherrypy

def get_lng():
    domain = cherrypy.request.base.lower().replace('http://', '')
    if domain.startswith('ru.'):
        return 'RU'
    return 'EN'
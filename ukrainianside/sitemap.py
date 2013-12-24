import datetime

from . import engine


def getSitemap():
    #now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    
    sitemap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
        "<urlset xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd\" xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"\
            "<url>" \
                "<loc>http://ukrainianside.com/</loc>" \
                "<lastmod>" + now + "</lastmod>" \
                "<changefreq>daily</changefreq>" \
                "<priority>1.0</priority>" \
            "</url>"
    
    aticles = engine.article.getAll() 
    
    for a in aticles:
        sitemap += "<url>" \
                "<loc>" + engine.article.getQuotedUrlByAlias(a.alias) + "</loc>" \
                "<lastmod>" + now + "</lastmod>" \
                "<changefreq>daily</changefreq>" \
                "<priority>1.0</priority>" \
            "</url>"

    sitemap += "</urlset>"
    
    return sitemap
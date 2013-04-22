import html5lib
import pycurl
from StringIO import StringIO
import time
from xml.etree import cElementTree as ET
import multiprocessing

htmlparser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("etree",ET),namespaceHTMLElements=False)
def GetHtmlByCurl(url):
    global htmlparser
    b=GetHttpByCurl(url)
    if b==None:
        return None
    try:
        doc=htmlparser.parse(b)
    except Exception,e:
        print e
        return None
    return doc
htmlparser2=html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"),namespaceHTMLElements=False)
def GetMiniDomByCurl(url):
    global htmlparser2
    b=GetHttpByCurl(url)
    if b==None:
        return None
    try:
        doc=htmlparser2.parse(b)
        if doc.documentElement.attributes.getNamedItem('xmlns'):
            doc.documentElement.attributes.removeNamedItem('xmlns')
    except Exception,e:
        print e
        return None
    return doc
def GetHttpByCurl(url):
    curl=pycurl.Curl()
    if isinstance(url,unicode):
        url=url.encode('utf8')
    curl.setopt(pycurl.URL,url)
    curl.setopt(pycurl.ENCODING,'gzip')
    curl.setopt(pycurl.TIMEOUT, 20)
    b = StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, b.write)
    for i in xrange(10):
        try:
            curl.perform()
            break
        except Exception,e:
            print e
            time.sleep(10)
    if curl.getinfo(pycurl.HTTP_CODE)!=200:
        return None
    b.seek(0)
    return b

def RunInMutiProcess(MutiProcFunction,GetNewWork,ProcResult):
    pool=multiprocessing.Pool()
    results=[]

    while True:
        if len(results)>20:
            time.sleep(0.2)
        else:
            pair=GetNewWork()
            if pair:
                results.append(pool.apply_async(MutiProcFunction,pair))
            elif len(results)==0:
                break
            else:
                time.sleep(0.1)
        for res in results:
            if res.ready():
                results.remove(res)
                if res.successful() and ProcResult is not None:
                    proc_result=res.get()
                    ProcResult(proc_result)
    pool.close()
    pool.join()
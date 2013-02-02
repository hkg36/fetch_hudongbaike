#-*-coding:utf-8-*-
import html5lib
import pycurl
from StringIO import StringIO
import xpath

curl=pycurl.Curl()
curl.setopt(pycurl.URL,'http://fenlei.baike.com/%E6%96%87%E9%9D%A9%E6%97%B6%E6%9C%9F%E7%89%B9%E5%AE%9A%E4%BA%BA%E7%BE%A4%E7%A7%B0%E8%B0%93/')
curl.setopt(pycurl.ENCODING,'gzip')
curl.setopt(pycurl.TIMEOUT, 20)
b = StringIO()
curl.setopt(pycurl.WRITEFUNCTION, b.write)
curl.perform()
b.seek(0)
htmlparser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"),namespaceHTMLElements=False)
dom=htmlparser.parse(b)
if dom.documentElement.attributes.getNamedItem('xmlns'):
    dom.documentElement.attributes.removeNamedItem('xmlns')
res=xpath.find("//div",dom)
print len(res)
pass
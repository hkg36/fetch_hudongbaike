#-*-coding:utf-8-*-
import urllib
import urllib2
import json
import re

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
def HTTPPost(url, data):
    req = urllib2.Request(url)
    data = urllib.urlencode(data)
    #enable cookie
    response = opener.open(req, data,timeout=20)
    if response.code==200:
        js=json.load(response)
        return js
    raise Exception('read fail')

def ReadFenleiAllWordPage(word):
    for i in xrange(5):
        try:
            if isinstance(word,unicode):
                word=word.encode('utf8')
            res=HTTPPost("http://fenlei.baike.com/categorySpecialTopicAction.do?action=showDocInfo",{'categoryName':word,'pagePerNum':1000,'pageNow':1})
            list=res.get('list')
            wordlist=[]
            if list is not None:
                for one in list:
                    url=one.get('title_url')
                    res=re.match('^http://www.baike.com/wiki/(?P<word>[^\?&\/]*)',url)
                    if res:
                        word=res.group('word')
                        word=urllib.unquote(word.encode('utf8'))
                        if isinstance(word,unicode)==False:
                            word=word.decode('utf8')
                        wordlist.append(word)
            return wordlist
        except Exception,e:
            print 'fatch all page error:',e
            continue
    return []
if __name__ == '__main__':
    wordlist=ReadFenleiAllWordPage('无线通信')
    for word in wordlist:
        print word
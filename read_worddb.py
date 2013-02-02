#-*-coding:utf-8-*-
import tools

import sqlite3
import bsddb3
import gzip
import html5lib
import json
import io
import re
import codecs
import multiprocessing
import time
import gzip
from xml.etree import cElementTree

htmlparser=html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("etree",cElementTree),namespaceHTMLElements = False)
def ProcessWord(pair):
    try:
        word=pair[0].decode('utf8')
        groups=[]
        doc=htmlparser.parse(gzip.GzipFile(fileobj=io.BytesIO(pair[1])))
        if doc is not None:
            res=doc.findall(".//div[@class='place']/p[@id='openCatp']/a")
            if res is not None:
                for one in res:
                    groups.append(one.get('title').strip())
            res=doc.find(".//div[@class='w-990']/div[@class='l w-640']/div[@class='content-h1']/h1")
            if res is not None:
                word=res.text
        spword=re.search(u'《?(?P<word>[^》\[]*)》?(\[(?P<ex>[^\]]*)\])?',word)
        if spword:
            word=spword.group('word')
            ex=spword.group('ex')
            if ex:
                groups.append(ex)
        return (word,groups)
    except Exception,e:
        return (None,str(e))

def ReadWordDb():
    home_dir='data/dictdb'
    dbenv = bsddb3.db.DBEnv()
    dbenv.open(home_dir, bsddb3.db.DB_CREATE | bsddb3.db.DB_INIT_MPOOL |
                         bsddb3.db.DB_INIT_LOCK | bsddb3.db.DB_THREAD |bsddb3.db.DB_INIT_TXN|
                         bsddb3.db.DB_RECOVER)
    db = bsddb3.db.DB(dbenv)
    db.open('maindb.db','main',bsddb3.db.DB_BTREE,bsddb3.db.DB_CREATE, 0666)
    dbc=db.cursor()

    sqlcon=sqlite3.connect('data/group.db')

    def GetNextWork():
        pair=dbc.get(bsddb3.db.DB_NEXT)
        return (pair,)
    def ProcResult(res):
        word,groups=res
        if word is not None:
            try:
                word_attr=words.get(word)
                if word_attr:
                    oldset=set(word_attr['group'])
                    oldset.update(groups)
                    words[word]={'group':list(oldset)}
                else:
                    words[word]={'group':groups}
                print word,json.dumps(groups,ensure_ascii=False)
            except Exception,e:
                print word,'failed',e
                sqlcon.execute('update wordlist set info_read=0 where word=?',(word,))


    words={}

    tools.RunInMutiProcess(ProcessWord,GetNextWork,ProcResult)

    word_out=gzip.open('data/hudongbaike_groupofword.txt.gz','w')
    json.dump(words,word_out)
    word_out.close()
if __name__ == '__main__':
    ReadWordDb()
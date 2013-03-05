#-*-coding:utf-8-*-
import tools

import sqlite3
import re
import urllib
import xpath
import html5lib

def ProcessWork(id,groupword):
    allword=[]
    if groupword:
        doc=tools.GetHtmlByCurl('http://fenlei.baike.com/%s/list/'%(urllib.quote(groupword.encode('utf8')),))
        if doc:
            node_a_list=doc.findall(".//dl[@class='link_blue line-25 zoom']/dd/a")
            if node_a_list:
                for node_a in node_a_list:
                    is_red=node_a.get('class')==u"link_red"
                    word=None
                    if is_red:
                        onclick=node_a.get('onclick')
                        found=re.search("'(?P<word>[^']*)'",onclick)
                        if found:
                            word=found.group('word')
                            word=urllib.unquote(word.encode('utf8'))
                            if isinstance(word,unicode)==False:
                                word=word.decode('utf8')
                    else:
                        href=node_a.get('href')
                        if href==None:
                            continue
                        found=re.search('http://www.baike.com/wiki/(?P<word>[^/\?\&]*)',href)
                        if found:
                            word=found.group('word')
                            word=urllib.unquote(word.encode('utf8'))
                            if isinstance(word,unicode)==False:
                                word=word.decode('utf8')
                    if word:
                        allword.append((word,id,is_red))
    return (id,groupword,allword)

class FetchWordList:
    def __init__(self):
        self.wordlist=[]
        self.work_fetch=None
        self.max_id=0

    def ProcessRes(self,res):
        id,groupword,allword=res
        if len(allword)>0:
            self.groupc.executemany('insert or ignore into wordlist(word,parent,isred) values(?,?,?)',allword)
        self.groupc.execute('update groupword set wordlist_checked=1 where id=?',(id,))
        print "%d %s finish"%(id,groupword)
        self.grouplist.commit()
    def GetNextWork(self):
        if len(self.wordlist)==0:
            self.groupc.execute('select id,word from groupword where wordlist_checked=0 and id>? order by id limit 20',(self.max_id,))
            for id,word in self.groupc:
                self.max_id=max(self.max_id,id)
                self.wordlist.append((id,word))
            if len(self.wordlist)==0:
                return None
        return self.wordlist.pop()
    def Run(self):
        self.grouplist=sqlite3.connect('data/group.db')
        try:
            self.grouplist.execute('alter table groupword add column wordlist_checked int default 0')
        except Exception,e:
            print e

        self.groupc=self.grouplist.cursor()
        tools.RunInMutiProcess(ProcessWork,self.GetNextWork,self.ProcessRes)

if __name__ == '__main__':
    FetchWordList().Run()
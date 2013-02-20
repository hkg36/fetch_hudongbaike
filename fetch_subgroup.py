#-*-coding:utf-8-*-
import tools

import sqlite3
import re
import urllib
import fetch_fenleipage

def ProcessWork(id,groupword):
    doc=tools.GetHtmlByCurl('http://fenlei.baike.com/%s/'%(urllib.quote(groupword.encode('utf8')),))
    new_words=[]
    new_fenlei=[]
    word_parent=None
    fun_res=(id,groupword,new_words,new_fenlei,word_parent)
    if doc==None:
        return fun_res

    link_list=doc.findall(".//a")
    for onelink in link_list:
        href=onelink.get('href')
        if href is None:
            continue
        res=re.match('^http://www.baike.com/wiki/(?P<word>.*)$',href)
        if res:
            word=res.group('word')
            word=urllib.unquote(word.encode('utf8'))
            if isinstance(word,unicode)==False:
                word=word.decode('utf8')
            new_words.append(word)

    new_words.extend(fetch_fenleipage.ReadFenleiAllWordPage(groupword))

    sub_class_name=doc.findall(".//div[@class='content bor-no']/div[@class='f_2']/div[@class='sort']/h3")
    sub_class=doc.findall(".//div[@class='content bor-no']/div[@class='f_2']/div[@class='sort']/p")
    for index in xrange(len(sub_class_name)):
        g_name=sub_class_name[index].text.strip()
        if g_name==u'父分类':
            sub_class2=sub_class[index]
            sub_a=sub_class2.findall('a')
            parent_groups=[]
            for node_a in sub_a:
                href=node_a.get('href')
                if href==None:
                    continue
                found=re.search(u'http://[^/]*/(?P<word>[^/]*)/?',href)
                if found:
                    word=found.group('word')
                    word=urllib.unquote(word.encode('utf8'))
                    if isinstance(word,unicode)==False:
                        word=word.decode('utf8')
                    parent_groups.append(word)
            word_parent=','.join(parent_groups)

        elif g_name==u'子分类':
            sub_class2=sub_class[index]
            sub_a=sub_class2.findall('a')
            for node_a in sub_a:
                href=node_a.get('href')
                if href==None:
                    continue
                found=re.search(u'http://[^/]*/(?P<word>[^/]*)/?',href)
                if found:
                    word=found.group('word')
                    word=urllib.unquote(word.encode('utf8'))
                    if isinstance(word,unicode)==False:
                        word=word.decode('utf8')
                    new_fenlei.append(word)
                    print 'new group %s'%word
    return fun_res
class FetchSubGroup:
    def __init__(self):
        self.grouplist=sqlite3.connect('data/group.db')
        try:
            self.grouplist.execute('alter table groupword add column sub_group_checked int default 0')
        except Exception,e:
            print e
        try:
            self.grouplist.execute('alter table groupword add column parent_group varchar(1024) default null')
        except Exception,e:
            print e
        self.groupc=self.grouplist.cursor()

        self.grouptocheck=[]
    def GetNextWork(self):
        if len(self.grouptocheck)==0:
            self.groupc.execute('select id,word from groupword where sub_group_checked=0')
            for id,word in self.groupc:
                self.grouptocheck.append((id,word))
            if len(self.grouptocheck)==0:
                return None
        return self.grouptocheck.pop()
    def ProcessResult(self,res):
        id,groupword,new_words,new_fenlei,word_parent=res
        if len(new_words):
            self.groupc.executemany('insert or ignore into wordlist(word,parent,isred) values(?,?,0)',[(word,id) for word in new_words])
        if word_parent and len(word_parent):
            self.groupc.execute('update groupword set parent_group=? where id=?',(word_parent,id))
        if len(new_fenlei):
            self.groupc.executemany('insert or ignore into groupword(word,parent) values(?,?)',[(word,id) for word in new_fenlei])

        self.groupc.execute('update groupword set sub_group_checked=1 where id=?',(id,))
        print "%d %s finished"%(id,groupword)
        self.grouplist.commit()
    def Run(self):
        tools.RunInMutiProcess(ProcessWork,self.GetNextWork,self.ProcessResult)
        self.grouplist.commit()
if __name__ == '__main__':
    FetchSubGroup().Run()
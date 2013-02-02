#-*-coding:utf-8-*-
import tools
import urllib
import sqlite3
import re
import xpath
import html5lib
def fetchRoot():
    doc=tools.GetHtmlByCurl("http://fenlei.baike.com/")
    alltable=doc.findall(".//div[@class='bor-e1 table']/div[@class='td w-578']")

    groups={}
    for table in alltable:
        allsub1=table.findall("dl[@class='w-160']")
        allsub2=table.findall("dl[@class='w-160 bor-no']")
        allsub1.extend(allsub2)
        for allsub in allsub1:
            master=allsub.find("dt/a")
            href=master.get('href')
            found=re.search('http://fenlei.baike.com/(?P<word>[^/]*)/?',href)
            if found:
                word=found.group('word')
                word=urllib.unquote(word.encode('utf8'))
                if isinstance(word,unicode)==False:
                    word=word.decode('utf8')
                master=word
            else:
                continue
            print master,'found'

            sublink=allsub.findall("dd/a")
            subname=[]
            for sl in sublink:
                href=sl.get('href')
                if href==None:
                    continue
                found=re.search('http://fenlei.baike.com/(?P<word>[^/]*)/?',href)
                if found:
                    word=found.group('word')
                    word=urllib.unquote(word.encode('utf8'))
                    if isinstance(word,unicode)==False:
                        word=word.decode('utf8')
                    subname.append(word)

                    print '%s found'%word
            groups[master]=subname

    grouplist=sqlite3.connect('data/group.db')
    grouplist.execute('create table if not exists groupword(id INTEGER PRIMARY KEY AUTOINCREMENT,word varchar(256) not null unique,parent int not null default 0,isred int default 0)')
    grouplist.execute('create table if not exists wordlist(id INTEGER PRIMARY KEY AUTOINCREMENT,word varchar(256) not null unique,parent int not null,isred int default 0,info_read int default 0)')
    groupc=grouplist.cursor()
    for key in groups:
        vlist=groups[key]
        groupc.execute('insert or ignore into groupword(word) values(?)',(key,))
        parentid=groupc.lastrowid
        for v in vlist:
            groupc.execute('insert or ignore into groupword(word,parent) values(?,?)',(v,parentid))
    grouplist.commit()
if __name__ == '__main__':
    fetchRoot()
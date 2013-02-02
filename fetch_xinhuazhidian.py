#-*-coding:utf-8-*-
import tools
import sqlite3
import xpath
import json
import codecs
import re
if __name__ == '__main__':
    db=sqlite3.connect('data/xinhuazhidian.db')
    db.execute('create table if not exists root(url varchar(1024) not null primary key,checked int default 0)')
    db.execute('create table if not exists sub1(url varchar(1024) not null primary key,word varchar(10) not null,checked int default 0)')
    db.execute('create table if not exists sub2(url varchar(1024) not null primary key,checked int default 0)')
    db.execute('create table if not exists words(url varchar(1024) not null primary key,word varchar(20) unique)')
    dbc=db.cursor()
    doc=tools.GetMiniDomByCurl('http://xh.5156edu.com/pinyi.html')
    list1=xpath.find("//table[@id='table1']/tbody/tr/td/table/tbody/tr/td/a",doc)
    for one in list1:
        dbc.execute('insert or ignore into root(url) values(?)',(one.getAttribute('href'),))
    db.commit()

    dbc.execute('select url from root where checked=0')
    tocheck=[]
    for url, in dbc:
        tocheck.append(url)
    for url in tocheck:
        doc=tools.GetMiniDomByCurl('http://xh.5156edu.com/'+url)
        links=xpath.find("//font[@class='font_14' and @color='red']/..",doc)
        for link in links:
            href=link.getAttribute('href')
            if href is None:
                continue
            text=[one.data for one in xpath.find("font[@class='font_14' and @color='red']/text()",link)]
            text=''.join(text)
            print href,text
            dbc.execute('insert or ignore into sub1(url,word) values(?,?)',(href,text))
            pass
        dbc.execute('update root set checked=1 where url=?',(url,))
        db.commit()

    tocheck=[]
    dbc.execute('select url from sub1 where checked=0')
    for url, in dbc:
        tocheck.append(url)
    for url in tocheck:
        doc=tools.GetMiniDomByCurl('http://xh.5156edu.com'+url)
        links=xpath.find('//td/a',doc)
        for link in links:
            href=link.getAttribute('href')
            if re.match('/ciyu/[^\.]+\.html',href):
                print url,href
                dbc.execute('insert or ignore into sub2(url) values(?)',(href,))
        dbc.execute('update sub1 set checked=1 where url=?',(url,))
        db.commit()

    dbc.execute('select url from sub2 where checked=0')
    tocheck=[]
    for url, in dbc:
        tocheck.append(url)
    for url in tocheck:
        doc=tools.GetMiniDomByCurl('http://xh.5156edu.com'+url)
        linklist=xpath.find("//table[@style='word-break:break-all']/tbody/tr/td/a",doc)
        for link in linklist:
            href=link.getAttribute('href')
            t_word=link.firstChild.data
            print t_word,href
            dbc.execute('insert or ignore into words(url,word) values(?,?)',(href,t_word))
        dbc.execute('update sub2 set checked=1 where url=?',(url,))
        db.commit()

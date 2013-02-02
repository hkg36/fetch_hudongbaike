#-*-coding:utf-8-*-
import sqlite3
import tools
import re
import time
def FetchSinaNews():
    sqlcon=sqlite3.connect('data/sina_news.db')
    sqlcon.execute('create table if not exists sina_news(url varchar(1024) PRIMARY KEY,title varchar(1024),content text,checked int default 0)')
    sqlc=sqlcon.cursor()

    doc=tools.GetHtmlByCurl('http://www.sina.com.cn')
    if doc is None:
        return
    alist=doc.findall(".//a")
    for a in alist:
        href=a.get('href')
        if not isinstance(href,unicode):
            continue
        href=href.strip()
        if re.match('^http://.*\.sina\.com\.cn/.*html$',href):
            sqlc.execute('insert or ignore into sina_news(url) values(?)',(href,))
            print href
    sqlcon.commit()

    sqlc.execute('select url from sina_news where checked=0')
    urls=[]
    for url, in sqlc:
        urls.append(url)
    for url in urls:
        try:
            doc=tools.GetHtmlByCurl(url)
            h1_node=doc.find(".//h1[@id='artibodyTitle']")
            title=h1_node.text.strip()
            content_ps=doc.findall(".//div[@id='artibody']/p")
            bodys=[]
            for ps in content_ps:
                for ele in ps.iter():
                    if ele is not None and len(ele.text)>0:
                        pstr=ele.text.strip()
                        if len(pstr):
                            bodys.append(pstr)
            body=''.join(bodys)
            print 'get news:',title
            sqlcon.execute('update sina_news set title=?,content=?,checked=1 where url=?',(title,body,url))
        except Exception,e:
            print 'pass',url
            sqlcon.execute('update sina_news set checked=1 where url=?',(url,))
            continue
    sqlcon.commit()
if __name__ == '__main__':
    while True:
        try:
            FetchSinaNews()
        except Exception,e:
            print e
        time.sleep(30*60)
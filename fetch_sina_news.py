#-*-coding:utf-8-*-
import sqlite3
import re
import time
import QueueClient
from cStringIO import StringIO
import gzip
import html5lib
from xml.etree import cElementTree as ElementTree

Queue_User='spider'
Queue_PassWord='spider'
Queue_Server='124.207.209.57'
Queue_Port=None
Queue_Path='/spider'

class DefaultHttpTask(QueueClient.Task):
    htmlparser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"),namespaceHTMLElements=False)
    def __init__(self,url):
        QueueClient.Task.__init__(self)
        self.url=url
        self.request_headers={'url':url}
    def StepFinish(self,taskqueueclient):
        stream = StringIO(self.result_body)
        if self.result_headers.get('zip'):
            stream = gzip.GzipFile(fileobj=stream)
        htmlfile = self.htmlparser.parse(stream)
        self.result_body=htmlfile
class NewsHttpTask(DefaultHttpTask):
    def __init__(self,url,sqlcon):
        DefaultHttpTask.__init__(self,url)
        self.sqlcon=sqlcon
    def StepFinish(self,taskqueueclient):
        stream = StringIO(self.result_body)
        if self.result_headers.get('zip'):
            stream = gzip.GzipFile(fileobj=stream)
        htmlfile = self.htmlparser.parse(stream)
        self.result_body=htmlfile

        try:
            h1_node=htmlfile.xpath("//h1[@id='artibodyTitle']")[0]
            title=h1_node.text.strip()
            content_ps=htmlfile.xpath("//div[@id='artibody']/p")
            bodys=[]
            for ps in content_ps:
                for ele in ps.iter():
                    if ele is not None and len(ele.text)>0:
                        pstr=ele.text.strip()
                        if len(pstr):
                            bodys.append(pstr)
            body=''.join(bodys)
            print 'get news:',title
            self.sqlcon.execute('update sina_news set title=?,content=?,checked=1 where url=?',(title,body,self.url))
        except Exception,e:
            print 'pass',self.url
            self.sqlcon.execute('update sina_news set checked=1 where url=?',(self.url,))
def FetchSinaNews():
    sqlcon=sqlite3.connect('data/sina_news.db')
    sqlcon.execute('create table if not exists sina_news(url varchar(1024) PRIMARY KEY,title varchar(1024),content text,checked int default 0)')
    sqlc=sqlcon.cursor()

    client=QueueClient.TaskQueueClient(Queue_Server,Queue_Port,Queue_Path,Queue_User,Queue_PassWord,'net_request',True)
    client.AddTask(DefaultHttpTask('http://www.sina.com.cn'))
    header,doc=client.WaitResult()
    if doc is None:
        return
    alist=doc.xpath("//a")
    for a in alist:
        href=a.get('href')
        if not href:
            continue
        href=href.strip()
        if re.match('^http://.*\.sina\.com\.cn/.*html$',href):
            sqlc.execute('insert or ignore into sina_news(url) values(?)',(href,))
            print href
    sqlcon.commit()

    sqlc.execute('select url from sina_news where checked=0')
    for url, in sqlc:
        client.AddTask(NewsHttpTask(url,sqlcon))
    client.WaitResult()
    sqlcon.commit()
    client.Close()
if __name__ == '__main__':
    while True:
        try:
            FetchSinaNews()
        except Exception,e:
            print e
        time.sleep(30*60)
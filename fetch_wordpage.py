#-*-coding:utf-8-*-
import tools

import sqlite3
import bsddb3,os
import urllib
import gzip
from cStringIO import StringIO

def ProcessWork(id,word):
    data=tools.GetHttpByCurl('http://www.baike.com/wiki/%s'%(urllib.quote(word.encode('utf8')),))
    if data:
        out = StringIO()
        f = gzip.GzipFile(fileobj=out, mode='w')
        f.write(data.getvalue())
        f.close()
        return (id,word,out.getvalue())
    else:
        return (id,word,None)
class FetchWordPage:
    def __init__(self):
        home_dir='data/dictdb'
        try:
            os.mkdir(home_dir)
        except Exception,e:
            print e
        self.dbenv = bsddb3.db.DBEnv()
        self.dbenv.open(home_dir, bsddb3.db.DB_CREATE | bsddb3.db.DB_INIT_MPOOL |
                             bsddb3.db.DB_INIT_LOCK | bsddb3.db.DB_THREAD |bsddb3.db.DB_INIT_TXN|
                             bsddb3.db.DB_RECOVER)
        self.db = bsddb3.db.DB(self.dbenv)
        self.db.open('maindb.db','main',bsddb3.db.DB_BTREE,bsddb3.db.DB_CREATE, 0666)

        self.sqlcon=sqlite3.connect('data/group.db')
        self.sqlc=self.sqlcon.cursor()

        self.wordlist=[]
    def GetNextWork(self):
        if len(self.wordlist)==0:
            self.sqlc.execute('select id,word from wordlist where info_read=0 and isred=0 limit 30')
            for id,word in self.sqlc:
                self.wordlist.append((id,word))
            if len(self.wordlist)==0:
                return None
        return self.wordlist.pop()
    def ProcResult(self,res):
        id,word,data=res
        if data!=None:
            self.db.put(word.encode('utf8'),data)
            self.dbenv.txn_checkpoint()
        self.sqlc.execute('update wordlist set info_read=1 where id=?',(id,))
        self.sqlcon.commit()
        print "%d %s finish"%(id,word)

    def Run(self):
        tools.RunInMutiProcess(ProcessWork,self.GetNextWork,self.ProcResult)
        self.dbenv.log_archive(bsddb3.db.DB_ARCH_REMOVE)

if __name__ == '__main__':
    FetchWordPage().Run()
#-*-coding:utf-8-*-
import sqlite3
import codecs
import re
import gzip
sqlcon=sqlite3.connect('data/group.db')
sqlc=sqlcon.cursor()
sqlc.execute('select distinct(word) from (select word from groupword union select word from wordlist) a')

word_set=set()
for word, in sqlc:
    spword=re.search(u'《?(?P<word>[^》\[]*)》?(\[(?P<ex>[^\]]*)\])?',word)
    if spword:
        word=spword.group('word')
        if re.match(u'^[\u0000-\u00FF]*$',word):
            continue
        word_set.update(re.split('[A-Za-z0-9\s]*',word))

sqlcon=sqlite3.connect('data/xinhuazhidian.db')
sqlc=sqlcon.cursor()
sqlc.execute('select word from words')
for word, in sqlc:
    words=re.split('[，\s]+',word)
    word_set.update(words)

word_set.remove('')
print 'loaded'
f=gzip.open('data/hudongbaike_allword.txt.gz','w')
info = codecs.lookup('utf-8')
f = codecs.StreamReaderWriter(f, info.streamreader, info.streamwriter)
for word in word_set:
    try:
        print >>f,word
    except Exception,e:
        print word,e
f.close()
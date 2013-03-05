import all_root
import fetch_subgroup
import fetch_wordlist
import fetch_wordpage
import sqlite3
import read_worddb

def ResetDb():
    sqlcon=sqlite3.connect('data/group.db')
    sqlc=sqlcon.cursor()
    try:
        sqlc.execute('update groupword set sub_group_checked=0,wordlist_checked=0')
        #sqlc.execute('update wordlist set info_read=0')
        sqlcon.commit()
    except Exception,e:
        print e
    finally:
        sqlc.close()
        sqlcon.close()
#ResetDb()
all_root.fetchRoot()
fetch_subgroup.FetchSubGroup().Run()
fetch_wordlist.FetchWordList().Run()
fetch_wordpage.FetchWordPage().Run()
read_worddb.ReadWordDb()
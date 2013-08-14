#-*-coding:utf-8-*-
import sqlite3
import codecs
if __name__ == '__main__':
    db=sqlite3.connect('data/group.db')
    dbc=db.cursor()
    dbc.execute('select id,word,parent_group from groupword')
    all_word={}
    for id,word,parent_group in dbc:
        if parent_group:
            all_word[id]={'word':word,'groups':set(parent_group.split(','))}
        else:
            all_word[id]={'word':word}

    select_group={}

    to_find_word_list=set([u'育儿'])

    while True:
        new_select_group={}
        for id in all_word:
            value=all_word[id]
            group=value.get('groups')

            if group and to_find_word_list & group:
                new_select_group[id]=value
        if len(new_select_group)==0:
            break
        to_find_word_list.clear()
        for id in new_select_group:
            value=new_select_group[id]
            to_find_word_list.add(value['word'])
        select_group.update(new_select_group)

    class_list=','.join(['%d'%one for one in select_group.keys()])

    dbc.execute('select word from wordlist where parent in(%s)'%class_list)
    outfile=codecs.open('data/out_group_word.txt','w','gb2312',errors='ignore')
    for word, in dbc:
        print >>outfile,word
    outfile.close()

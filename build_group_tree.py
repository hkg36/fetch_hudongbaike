#-*-coding:utf-8-*-
import sqlite3
import codecs
import re
class GroupTree:
    class WordGroupInfo:
        parent_group=None
        groupname=None
        parent_obj=[]
        def __str__(self):
            return self.groupname
    def BuildTree(self):
        sqlcon=sqlite3.connect('data/group.db')
        sqlc=sqlcon.cursor()
        sqlc.execute('select word,parent_group from groupword')

        group_dic={}
        for word,parent_group in sqlc:
            if parent_group:
                parent_group=parent_group.split(u',')
                obj=self.WordGroupInfo()
                obj.parent_group=parent_group
                obj.groupname=word
                obj.parent_obj=[]
                group_dic[word]=obj
        for word in group_dic:
            obj=group_dic[word]
            for pg in obj.parent_group:
                po=group_dic.get(pg)
                if po:
                    obj.parent_obj.append(po)

        self.group_dic=group_dic

    def FindAllParent(self,groupname):
        foundgroup=set()
        ginfo=self.group_dic.get(groupname)
        if ginfo is None:
            return None
        foundgroup.add(ginfo)
        self._findparentgroup(ginfo,foundgroup)
        return foundgroup
    def _findparentgroup(self,ginfo,foundgroups):
        tofind=[]
        for obj in ginfo.parent_obj:
            if obj not in foundgroups:
                tofind.append(obj)
                foundgroups.add(obj)
        for tf in tofind:
            self._findparentgroup(tf,foundgroups)

if __name__ == '__main__':
    tree=GroupTree()
    tree.BuildTree()
    foundgroup=tree.FindAllParent(u'乔木')
    for fg in foundgroup:
        print str(fg)
    pass
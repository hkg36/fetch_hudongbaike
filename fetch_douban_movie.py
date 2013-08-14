#-*-coding:utf-8-*-
import tools
import os,sys
import sqlite3
if __name__ == '__main__':
    data_root_dir='/app_data/douban'
    if os.path.exists(data_root_dir)==False:
        os.mkdir(data_root_dir)

    doc=tools.GetHtmlByCurl('http://movie.douban.com/tag/')
    all=doc.findall(".//table[@class='tagCol']/tbody/tr/td/a")
    conn=sqlite3.connect(os.path.join(data_root_dir,'douban_movie.sqlite'))
    conn.execute('create table if not exists movie_class(url varchar(1024),lastcheck datetime,PRIMARY KEY(url))')


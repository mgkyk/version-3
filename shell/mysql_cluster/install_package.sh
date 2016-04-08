#!/bin/bash
#
# author: ChuXiaokai
# date: 2016/4/1    Happy April Fool's Day

# intall tar package
useradd -s /sbin/nologin -M mysql
mkdir -p /usr/local/mysql
mkdir -p /data/mysqldb 
mkdir /data/mysql
tar xvf mysql-cluster-gpl-7.2.8.tar.gz
cd mysql-cluster-gpl-7.2.8
cmake -DCMAKE_INSTALL_PREFIX=/usr/local/mysql \
-DMYSQL_UNIX_ADDR=/data/mysql/mysql.sock \
-DDEFAULT_CHARSET=utf8 \
-DDEFAULT_COLLATION=utf8_general_ci \
-DWITH_EXTRA_CHARSETS:STRING=utf8,gbk \
-DWITH_INNOBASE_STORAGE_ENGINE=1 \
-DWITH_READLINE=1 \
-DENABLED_LOCAL_INFILE=1 \
-DMYSQL_DATADIR=/data/mysql/ \
-DMYSQL_USER=mysql \
-DMYSQL_TCP_PORT=3306

make && make install


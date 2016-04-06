#!/bin/bash
#
# author: ChuXiaokai
# date: 2016/3/30

## create group and user
useradd -s /sbin/nologin -M mysql

## create dir for the mysql
mkdir -p /usr/local/mysql
mkdir -p /data/mysqldb 

## make mysql
tar -zxvf mysql-5.5.20.tar.gz

cd mysql-5.5.20

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

## priviledge
chown -R root.mysql /usr/local/mysql
chown -R mysql.mysql /usr/local/mysql/data
bash scripts/mysql_install_db --user=mysql --basedir=/usr/local/mysql
/usr/local/mysql/scripts/mysql_install_db --basedir=/usr/local/mysql --datadir=/usr/local/mysql/data --user=mysql
cp support-files/my-medium.cnf /etc/my.cnf
cp support-files/mysql.server /etc/init.d/mysqld
chmod +x /etc/init.d/mysqld

## revise
sed -i '$a [mysqld]\nuser=mysql\ncharacter_set_server=utf8\ndatadir=/usr/local/mysql/data\nbasedir=/usr/local/mysql' /etc/my.cnf

/etc/init.d/mysqld start
echo "mysql start"

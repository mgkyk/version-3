#!/bin/bash
#
# author: ChuXiaokai
# Date: 2016/4/1    Happy April Fool's Day

# mkdir
useradd -s /sbin/nologin -M mysql
mkdir -p /usr/local/mysql
mkdir -p /data/mysqldb 
mkdir -p /data/mysql

# priviledge
cd mysql-cluster-gpl-7.2.8
chown -R root.mysql /usr/local/mysql
chown -R mysql.mysql /usr/local/mysql/data

# source
/usr/local/mysql/scripts/mysql_install_db --basedir=/usr/local/mysql --datadir=/data/mysql/ --user=mysql

# copy and revise my.cnf
cp support-files/my-medium.cnf /etc/my.cnf
cp support-files/mysql.server /etc/init.d/mysqld
chmod +x /etc/init.d/mysqld
echo -e "\n\n[MYSQLD]\nuser=mysql\ncharacter_set_server=utf8\nndbcluster\nndb-connectstring=$1\ndefault-storage-engine=ndbcluster\ndatadir=/usr/local/mysql/data\nbasedir=/usr/local/mysql\n[MYSQL_CLUSTER]\nndb-connectstring=$1" >> /etc/my.cnf

# source
bash scripts/mysql_install_db --user=mysql --basedir=/usr/local/mysql

# init and start
/usr/local/mysql/bin/ndbd –initial
/etc/init.d/mysqld start

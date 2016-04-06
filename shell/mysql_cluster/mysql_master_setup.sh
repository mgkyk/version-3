#! /bin/bash
#
# author: ChuXiaokia
# date: 2016/4/1    Happy April Fool's Day

# mkdir

if [ ! -d "/data" ];then
    mkdir /data
fi

if [ ! -d "/data/mysql-cluster" ];then
    mkdir –p /data/mysql-cluster/ 
fi

if [ ! -d "/data/mysql" ];then
    mkdir /data/mysql/
fi

# revise the config.ini
if [ ! -d "/data/mysql-cluster/config.ini" ]; then
    touch /data/mysql-cluster/config.ini
fi

num_ndbd=`expr $# - 1`
 
echo -e "[ndbd default]\nNoOfReplicas=$num_ndbd\nDataMemory=80M\nIndexMemory=18M\n" >> /data/mysql-cluster/config.ini
echo -e "[ndb_mgmd]\nId=1\nHostname=$1\ndatadir=/data/mysql/\n" >> /data/mysql-cluster/config.ini
echo "The number of the param is $#"


id=2
j=0
for i in $@;
do
    j=`expr $j + 1`
    echo "j="$j
    echo $i
    if (( $j != 1 )); then
        echo -e  "[ndbd]\nId=$id\nHostname=$i\ndatadir=/data/mysql/\n" >> /data/mysql-cluster/config.ini
        # sed -i "$a [ndbd]\nId=$id\nHostname=$i\ndatadir=/data/mysql/\n" /data/mysql-cluster/config.ini
        id=`expr $id + 1`
        echo -e  "[mysqld]\nId=$id\nHostname=$i\n" >> /data/mysql-cluster/config.ini
        id=`expr $id + 1`
    fi
done

echo -e "[MYSQLD]\n[MYSQLD]\n" >> /data/mysql-cluster/config.ini
#sed -i "$a [MYSQLD]\n[MYSQLD]" 

# source and init
/usr/local/mysql/bin/ndb_mgmd -f /data/mysql-cluster/config.ini

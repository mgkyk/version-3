#!/bin/bash
#
# author: ChuXiaokai
# date: 2016/4/1    Happy April Fool's Day

# parallel install mysql-cluster.tar.gz


SOURCE_PATH=/home/cxk/workspace/source
SHELL_PATH=/home/cxk/workspace/shell/mysql_cluster
master=$1
master_ip=$(docker inspect --format="{{.NetworkSettings.IPAddress}}" $1)
echo $master_ip, $master

for i in $@;
do
    {
     # copy file in the docker mc
     docker cp $SOURCE_PATH/mysql-cluster-gpl-7.2.8.tar.gz $i:/
     docker cp $SHELL_PATH/install_package.sh $i:/
     # exec the shells
     echo start installing mysql
     docker exec $i bash install_package.sh
     echo install mysql package SUCCESS
    }&
done
wait

# configuration setting
## the master node
echo "start configuring"
shift # param <<
docker cp $SHELL_PATH/mysql_master_setup.sh $master:/
b=$master_ip
for i in $*;
do
    echo container=$i
    b="$b"" $(docker inspect --format='{{.NetworkSettings.IPAddress}}' $i)"
done
echo param=$b
docker exec $master bash mysql_master_setup.sh $b
echo "configure master success"

## the slave node
for i in $@;
do
    {
        docker cp $SHELL_PATH/mysql_slave_setup.sh $i:/
        docker exec $i bash mysql_slave_setup.sh $master_ip
        echo "$i INSTALL SUCCESS"  
    }
done
wait

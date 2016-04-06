#!/bin/bash
stty -echo  # do not display echo

WORK_PATH=/home/cxk/workspace

# copy .tar.gz to the docker machine
docker cp $WORK_PATH/source/mysql-5.5.20.tar.gz $1:/

# copy shell to the docker machine
docker cp $WORK_PATH/shell/mysql_singlenode/mysql_server_setup.sh $1:/

# priviledge
# docker exec $1 chmod +x mysql_server_setup.sh

docker exec $1 bash mysql_server_setup.sh

stty echo  # display echo
echo "SUCCESS SETUP"

#!/bin/bash

## CPU
cpu_info=$(docker exec $1 uptime | gawk '{printf "numbers of user: %s, average load in 1, 5, 15 minutes: %s %s %s", $4, $8, $9, $10}')

## DISK
disk_info=$(docker exec $1 df -h | sed -n '/hosts/p' | gawk '{printf "total: %s, used: %s, available: %s", $2, $4, $5}')

## MEMORY
mem_info=$(docker exec $1 free -h | sed -n '2p' | gawk 'x = ($3 / $2) {printf "total: %s, free: %s, percent: %s", $2, $3, x}')

## CPu
idle_info=$(docker exec $1 vmstat 1 2 | sed -n '/[0-9]/p' | sed -n '2p' | gawk '{printf "IDLE: %s%", $15}')

echo $cpu_info
echo $disk_info
echo $mem_info
echo $idle_info

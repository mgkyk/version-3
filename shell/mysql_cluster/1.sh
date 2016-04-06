
d=$(docker inspect --format="{{.NetworkSettings.IPAddress}}" 2f6c053a3838)
echo $d

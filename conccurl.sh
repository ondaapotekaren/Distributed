#!/bin/bash
for i in `seq 1 5`; do
curl -d 'entry=a'${i} -X 'POST /board' 'http://10.0.212.242:63118' &
curl -d 'entry=c'${i} -X 'POST /board' 'http://10.0.212.242:63120' &
curl -d 'entry=d'${i} -X 'POST /board' 'http://10.0.212.242:63121' &
done
sleep 1
curl -d 'entry=b1' -X 'POST /board' 'http://10.0.212.242:63119' 
curl -d 'entry=b2' -X 'POST /board' 'http://10.0.212.242:63119' 
curl -d 'entry=b3' -X 'POST /board' 'http://10.0.212.242:63119' 
curl -d 'entry=b4' -X 'POST /board' 'http://10.0.212.242:63119' 
curl -d 'entry=b5' -X 'POST /board' 'http://10.0.212.242:63119' 


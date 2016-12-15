#!/bin/bash
for i in `seq 1 10`; do
curl -d 'entry=a'${i} -X 'POST /board' 'http://202.141.161.43:63159' &
curl -d 'entry=b'${i} -X 'POST /board' 'http://195.113.161.83:63159' &
curl -d 'entry=c'${i} -X 'POST /board' 'http://128.112.139.19:63159' &
done

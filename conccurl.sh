#!/bin/bash
for i in `seq 1 10`; do
curl -d 'entry=t'${i} -X 'POST /board' 'http://10.0.132.48:63118' &
curl -d 'entry=t'${i} -X 'POST /board' 'http://10.0.132.48:63119' &
curl -d 'entry=t'${i} -X 'POST /board' 'http://10.0.132.48:63120' &
done

#!/bin/bash
for i in `seq 1 10`; do
curl -d 'entry=t'${i} -X 'POST /board' 'http://129.16.24.216:63118' &
curl -d 'entry=t'${i} -X 'POST /board' 'http://129.16.24.216:63119' &
curl -d 'entry=t'${i} -X 'POST /board' 'http://129.16.24.216:63120' &
done

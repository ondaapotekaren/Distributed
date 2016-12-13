#!/bin/bash
for i in `seq 1 5`; do
curl -d 'entry=b'${i} -X 'POST' 'http://129.16.25.59:63120/board' &
curl -d 'entry=a'${i} -X 'POST' 'http://129.16.25.59:63118/board' &
curl -d 'entry=c'${i} -X 'POST' 'http://129.16.25.59:63119/board' &
done

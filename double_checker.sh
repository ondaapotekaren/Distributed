#!/bin/bash
curl -d 'entry=failed_double_check&entryID=2&vid=63120&sendclock=1&recclock=10' -X 'POST /neighbour/entries' 'http://129.16.25.57:63120'

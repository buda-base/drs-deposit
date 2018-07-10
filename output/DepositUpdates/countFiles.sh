#!/bin/bash
 for ff in *.csv ; do echo -n $ff ;  awk -F','  'BEGIN {c = 0 ; sz = 0;}{ c = c + $15; sz = sz + $NF ; } END{print c,sz }' $ff ; done

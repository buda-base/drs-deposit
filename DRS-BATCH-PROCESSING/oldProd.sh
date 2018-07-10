#!/usr/bin/env bash
 's/.*batch\(W.*\)\-.*/\1/' oldProd
 # takes
 # ./20180330/worksList2.18.09/batchW00EGS1018179-1/batch.xml
 # returns W00EGS1018179
 #
 # Look for the works in the DBWorks.csv
#  grep -f oldProdWorks DBWorks.csv > opwWithHOLLIS
#  grep -f oldProdWorks DBWorks.csv > opwWithHOLLIS
#
# How many lines in common?
#(py361) jimk@Druk:oldBatchesToDB$ comm -12 oldProdWorks.su opwHOLLIS.su  | wc
#    5541    5541   48760
# how manu lines ONLY in oldProdWorks
#(py361) jimk@Druk:oldBatchesToDB$ comm -23 oldProdWorks.su opwHOLLIS.su  | wc
#       0       0       0
# How many lines only in opwHOLLIS?
#(py361) jimk@Druk:oldBatchesToDB$ comm -13 oldProdWorks.su opwHOLLIS.su  | wc
#    3663    3663   34339
#(py361) jimk@Druk:oldBatchesToDB$ wc oldProdWorks.su opwHOLLIS.su *csv
#    5541    5541   48760 oldProdWorks.su
#    9204    9204   83099 opwHOLLIS.su
#   13767   27534  665354 DBWorks.csv
#   28512   42279  797213 total
# Note
#   (lines in common) + (lines only in opwHOLLIS) = lines in opwHOLLIS
# (5541 + 3663 = 9204)


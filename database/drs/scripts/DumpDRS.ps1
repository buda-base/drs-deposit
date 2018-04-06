#
# Dump drs. 
# Add routines
mysqldump --login-path=ubu1610 --opt --routines --databases drs --result-file=ubu1610.dump.sql

#
# To reload, 
# mysql ----
# mysql> source whatever

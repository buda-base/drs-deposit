$creds = $($args[0])
$db = $($args[1])

# DB
$backFile = "Northgate\bdrc\drs-deposit\database\" + $db + "\dump\"
$backupPath = Join-Path -Path $HOME -ChildPath $backFile
# See https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html
# Dump data separately from code

# DEBUG
# $backupPath += "XXX"

$dataFile= $backupPath + "data_only.sqldump"
$DDLFile = $backupPath + "DDL_only.sqldump"

# PS is so lame, you can't literalize parameters
# like
# $p = "--login-path=FRED"
# mysqldump $p ....."
# mysqldump  --login-path=$creds --hex-blob --no-create-info --databases $db --result-file=$dataFile
# mysqldump  --login-path=$creds --routines  --no-create-info --no-data --triggers --databases $db --result-file=$DDLFile
#
# Take 1:   triggers were fully qualified: fix was to update their DDL in the db
# Take 2:   Triggers in DDLFile were defined before tables they were to go with
#           Along the way, I noticed that the data file also referenced the tables before they were defined.
#           That's mostly ok, but I took out --no-create-info in the DDL definition
mysqldump  --login-path=$creds --hex-blob  --result-file=$dataFile $db
mysqldump  --login-path=$creds --routines --no-create-info --no-data --triggers --result-file=$DDLFile $db



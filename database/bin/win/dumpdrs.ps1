$creds = $($args[0])
$db = $($args[1])

# DB
$backFile = "Northgate\bdrc\drs-deposit\database\backup\" + $db
$backupPath = Join-Path -Path $HOME -ChildPath $backFile
# See https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html
# Dump data separately from code

$dataFile= $backupPath + "data_only.sqldump"
$DDLFile = $backupPath + "DDL_only.sqldump"

# PS is so lame, you can't literalize parameters
# like
# $p = "--login-path=FRED"
# mysqldump $p ....."
mysqldump  --login-path=$creds --hex-blob --no-create-info --databases $db --result-file=$dataFile
mysqldump  --login-path=$creds --routines --no-data --triggers --databases $db --result-file=$DDLFile

#!/usr/bin/awk -f
#
# Parse a series of email messages for error texts
# Each message boundary is defined to be on the email 'Date' header

#
# Begin an error text capture cycle
function initCycle(){
    thisDate = "";
    thisUser = "";
    thisBatchDir="";
    thisError="";
    thisReportId="";
    return 1
}
#
# Print pipe sep fields (text has colons)
# print ReportId, date, user, batchDirectory,Message 
function dumpCycle(inCycle) { 
    if (inCycle) {
	printf("%s|%s|%s|%s|%s|",
	       thisDate ,
	       thisReportId,
	       thisUser ,
	       thisBatchDir,
	       thisError);
	print outString;
    }
    return  0;
}

# trim leading and trailing whitespace
# Thank you Dr. Stack
# https://stackoverflow.com/questions/20600982/trim-leading-and-trailing-spaces-from-a-string-in-awk
function chop(inp){
    gsub(/^[ \t]+|[ \t]+$/,"",inp);
    return inp;
}

BEGIN {
    FS=":";
    userLabel = "^Drop Box";
    batchLabel = "^Batch Directory";
    errLabel = "^Message";
    dateLabel= "^Date";
    reportIdLabel = "^Report ID";

# Init without setting state
    initCycle();
    cycle = 0;

}
{

    if ($0 ~ dateLabel ) {
	dumpCycle(cycle);
	cycle = initCycle();
	thisDate = chop(substr($0,length(dateLabel)+1));
    }
   
    if ($0 ~ userLabel ) { thisUser = chop($2) ;}
    if ($0 ~ batchLabel ) { thisBatchDir = chop($2) ; }
    if ($0 ~ reportIdLabel ) { thisReportId = chop($2) ; }
    if ($0 ~ errLabel) {getline ; thisError = chop($0) ;}

#     if ($0 ~ userLabel ) { thisUser = $2 ;}
# if ($0 ~ userLabel ) { thisUser = $2 ;}
#     ($0 ~ batchLabel ) { print "Found a batch_"op"_ val="$2"_"};
#     if ($0 ~ errLabel) {getline ; errMessage = $0 ;  print "Found an error _"op"_ val=" errMessage; };


}
END {
    dumpCycle(1);
}

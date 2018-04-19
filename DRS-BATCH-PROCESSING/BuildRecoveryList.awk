#!/usr/bin/awk -f
#
# Fi checksum mismatch errors
# searches for batches in a list of source files,
# and then emits sftp commands to resend the damaged file.
#
# Usage:

# The args must come before the data file.
#
# Renaming BATCH_XML_FAIL to BATCH_XML invokes the load process.
function Usage() {
	print "Usage:  BuildRecoveryList -v ARG_OUTDIR=outDirName -v ARG_PREFIX=argPrefix -V ARG_SRCS=filePattern dataFile";
	print "where ARG_OUTDIR = destination directory for sets of sftp scripts"
	print "		 ARG_PREFIX is the prefix for sftp scripts"	
	print "		 ARG_SRCS is the filespec for a set of files which are parsed for batch names to recover - metacharacters "
	print "		 			must be quoted. such as  -v ARG_SRCS=\'frelm*\' to search in all files whose name begins with frelm" 
	print "		 dataFile is a list of batches. Can be free form, but you have to modify the main loop call to BuildSftpBatch"
	print "		 to pass in the batch name."

}
#


# Sample line    
# MD5 checksum mismatch for descriptor file  drs drsfs dropbox drs2_tbrcftp incoming batchW1KG9261-1 W1KG9261-I1KG9552 descriptor.xml, services reported CBE9B8ECC294890AC1DFCB3A6AD018F6 

# 
# Emit SFTP instructions to deposit specific files, as drven by sample input line
# you can't print BuildSftpBatch() >> filePath, so it has to be passed in
function BuildSftpBatch(filePath,batchNum,fileWhoseParentsWeFetch)
{  
	# print $13,$14,$15 ; 
#	print filePath,batchNum,fileWhoseParentsWeFetch, SRCS
	# SRCS is a file of batch directories, one per line
	cmd = " grep -h "batchNum " " SRCS ; 
	cmd | getline srcDir ;
	close(cmd);

#	print "cmd :" cmd ": srcDir :" srcDir ":"

	print "cd /incoming/" batchNum > filePath;

	# Get all the descriptors.xml in this patch and replace them
	# Find the parents of descriptor.xml
	getAllDesc = "find " srcDir " -type d -maxdepth 1 -mindepth 1";
  print "getAllDesc :" getAllDesc ;
	while ( ( getAllDesc | getline volume) > 0){
		volDir=volume
		gsub(".*/","",volDir)
		ftpRmDesc = sprintf("rm %s/%s",  volDir,fileWhoseParentsWeFetch );
		print ftpRmDesc  >>  filePath;
		ftpPutDescriptor = sprintf("put -P %s/%s %s/%s", volume, fileWhoseParentsWeFetch, volDir,fileWhoseParentsWeFetch );
#		print "volume :" volume " ftpPutDescriptor :" ftpPutDescriptor ":" ; #  >> filePath;
		print ftpPutDescriptor  >> filePath;
	}
	close(getAllDesc)

	# Finally, bring up a new batch.xml
	ftpRmCmd = sprintf("rm %s", BATCH_XML_FAIL);
	print ftpRmCmd >> filePath;

	ftpUpCmd = sprintf("put %s/%s", srcDir,BATCH_XML);

	print  ftpUpCmd >> filePath;
	print "quit" >> filePath;

	close(filePath);
}

BEGIN { 

	print "args ARG_OUTDIR :" ARG_OUTDIR   ": ARG_PREFIX :" ARG_PREFIX ":"

	if ( (ARG_PREFIX == "") || (ARG_OUTDIR == "") || (ARG_SRCS == "" ) ) {
		Usage()
		exit 1
	}
	FS = "[/ ,]";
	# SRCS = "../TodaysUploads*.txt ";
	SRCS = ARG_SRCS ;
	BATCH_XML = "batch.xml";
	BATCH_XML_FAIL = "batch.xml.failed";
	OUT_DIR = ARG_OUTDIR ; # "sftpCmds";
	FILE_PREFIX = OUT_DIR "/" ARG_PREFIX;

	c =  "mkdir " OUT_DIR;
	c | getline rc;
	close rc;
	fileCount = 0;

	print "out dir: " OUT_DIR " prefix: " FILE_PREFIX;
}

{
	if (NF)
	{
	 	fn = FILE_PREFIX fileCount ;
	 	 # This format is for the MD5 failure messages
	 	 # BuildSftpBatch(fn, $13, $15)
	 	 #
	 	 # this is just a list of failed batches.
	 	 BuildSftpBatch( fn, $1, "descriptor.xml" )

	 	fileCount++;
	 }
}

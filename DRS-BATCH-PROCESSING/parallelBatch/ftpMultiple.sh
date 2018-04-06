#!/bin/bash 
#
# launch and track a bunch of background tasks
# 
# Arguments:
#	1:  beginning worksList number
#   2.  Ending worksList number
# Dependencies:
#
# splitWorks.sh: runMultiple expects that splitWorks has created 
# a directory named ${WORKS_SRC} which contains
# a list of files named ${WORKS_LIST_FN}nnnn.txt where nnnn is any
# arbitrary integer.
# 
# If there are gaps in the sequence, makeOneDrs.sh fails, no big deal.
#
# Some constants
#
UNDERWAY_DIR=timing/underway
[ -d  $UNDERWAY_DIR ] || mkdir -p $UNDERWAY_DIR

RESULTS_DIR=timing/finishedRuns
[ -d  $RESULTS_DIR ] || mkdir -p $RESULTS_DIR

NO_VALUE='$@@<<no_value>>@@'
#end constants
#

ME=$(basename $0)

#----------------------------------------------------------------------
# Usage
#
function usage() {
	cat << USAGE
		synopsis: $ME -h  this message
		synopsis: $ME [ -u userFileName ] -w worksListPath
		synopsis: $ME  -U userName  -w worksListPrefix  wl1 [ wl2 =wl1] 
				
		run multiple lists of works in files '${worksListPath}{1..n}.txt'

		There are two use cases
		Mutiple paralllel logons of different users
		-u userFileName [optional] is a list of users of the host.
			This list controls a splitting of the works list into
			one file for each user, to support multiple parallel transfers
			to multiple accounts

			if userFileName is given, the argument to the 
			-w flag represents a single file which contains all the paths
			to be sent up. $ME divides the works list into one file 
			for each user in userFileName, and numbers them
			(dirname worksListPath)/basename worksListPath{1..n}.txt

		-w worksListPath
			if the two arguments wl1 [ wl2 ] are given, AND the -u flag is
			NOT given, then 
			* wl1 and wl2 stand for a range of integers which 
			  defines a set of files, and
			* the -w option is a pattern consisting
			of "directory name"/prefix. "directory name" is created if it does
			not exist. The files are created in the current directory if 
			worksListPath has no directory component. $ME sends the files
			worksListPath{1..n}.txt to the makeOneFtp.sh

			When the -u flag is not given, the sftp sending user is the last
			argument.

USAGE
}

#----------------------------------------------------------------------
# Noisily expire
#
function die() {
	rc=$1
	shift 1
	echo $@
	exit $rc
}

#----------------------------------------------------------------------
#
# use the flags to determine what's in the workslist
#
# Args: Uses the outer scope's variables:
# Reads:  	userList (file)
#			worksListPath (source of works)
#
# Writes:
#	in $worksListPath directory, $worksListPath (without file extension 1..n)
# 	One file for each user line in userList.
#
#   Populates:
#		the outer scope's sendingUsers array
#		the outer scope's $wl1 and $wl2 indices (the limits of the)
# 
function splitWorks() {
	declare worksDir=$(dirname $worksListPath) \
			worksFileName=$(basename $worksListPath)

	while read aUser ; do
		sendingUsers+=($aUser)
	done < $userListPath

	
	pushd ${worksDir}
	wl1=1
	wl2=${#sendingUsers[*]}

	splitWorks.sh -f ${wl2} $worksFileName
	ls 
	read -p "what you see" glurm

	popd
}



#
# h   elp
# u   serList
# w   orksListPath
while getopts hu:U:w: opt ; do
	echo "in getopts" $opt $OPTARG
	case $opt in
		u)
			userListPath=$OPTARG;
			[ -f $userListPath ] || { die 2 "${ME}:error:List of users file \'$userListPath\' must exist but does not" ; }
#			echo "$opt triggered, arg is $OPTARG aka $userListPath"
			;;
		U)
			ftpUser=$OPTARG
#			echo "$opt triggered, arg is $OPTARG aka $userListPath"
			;;
		w)

			worksListPath=$OPTARG
#			echo "$opt triggered, arg is $OPTARG aka $worksListPath"
			;;
		h)
			usage
			exit 0
			;;
	esac
done
shift $((OPTIND-1))


# if no args, bail

# if we dont have a user list, and we dont have any args,
# we're toast, and we're outta here


[ "${userListPath:-$NO_VALUE}"  == "$NO_VALUE" ] &&  [ "${1:-$NO_VALUE}"  == "$NO_VALUE" ] &&  { usage ; exit 1 ; }

# worksListPath required
worksListPath=${worksListPath:?${ME}:usage:worksListPath is empty, or -w flag not given}



if [ "${userListPath:-${NO_VALUE}}" != "$NO_VALUE" ] ; then
# splitWorks fills this in
	sendingUsers=()
	splitWorks

	# Fix up worksListPath to have one calling sequence. REM that worksListPath
	# for this case is a fully qualified file name, and in its directory 'splitWorks'
	# has created a number
	# of files with its prefix.
	# Now worksListPath must represent a file name template:
	worksListPath=${worksListPath%.*}
else

# Set default for wl2 if not given
	wl1=$1
	wl2=${2:-$wl1}

fi

# 
#
# the number of lines in  is the same as the 
# number of files to transfer.

# user index
ui=$((0))
export ui

for x in $(seq $wl1 $wl2 ); do
	#
	# do_real_work
	#
	# jsk 12.22.17 Put the iteration here where we can see it
	# Run each iteration in the background
	# jsk 21.I.18: shell scripts can be in ~/bin
	# Har: the autoincrement doesnt work when executing in background.

	# set up user either from the list or command line
	curFtpUser=${sendingUsers[$((ui++))]:-$ftpUser} 
	
	# Capture the user and the file they uploaded. We need this in reports
	printf "%s|%s\n" $curFtpUser  ${worksListPath}${x}.txt >> ${worksListPath}.UploadTrack.lst
	makeOneFtp.sh ${worksListPath}${x}.txt $UNDERWAY_DIR $RESULTS_DIR  $curFtpUser &
 
done

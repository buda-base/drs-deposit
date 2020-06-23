# Include this as a literal command set to get a running total 
# If you want to create a file, replace ARGV[1] with $1, and comment out the sumCount
# display 
# get the count of all the files in the parents of the file
# paths passed in
 {
    cmd = "find $(dirname " $1 ") -type f | wc -l" ;
    cmd | getline thisCount ;
     close(cmd);
     sumCount += thisCount;print $1 "|" thisCount "|" sumCount;

      }
#  END  { print sumCount  }

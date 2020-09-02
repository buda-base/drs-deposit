#! /bin/bash
#
#  Intended to be run on a DRS deropbox host
cd incoming
for b in batchW* ; do
	if [ -f $b/batch.xml.wait ]; then
		mv $b/batch.xml.wait $b/batch.xml
	fi
done
exit

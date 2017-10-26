#!/bin/bash


echo "Generating MARC XML from TBRC Marc Service..."


worksList=$1

DATE=`date +%Y-%m-%d`
marcRecords=$2/marc-$DATE.xml
echo "Creating $FILE" 

STAG="<collection xmlns='http://www.loc.gov/MARC21/slim' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd'>"		
 

echo opening doc
echo $STAG > $marcRecords

# for i in `cat $WORKLIST`; 
while IFS= read -r w <&3;
do
		echo writing $w
		WORK="http://tbrc.org/public?module=work&query=marc&args=$w"
		curl $WORK >> $marcRecords
done 3< "$worksList"

ETAG="</collection>"

echo closing doc
echo $ETAG >> $marcRecords

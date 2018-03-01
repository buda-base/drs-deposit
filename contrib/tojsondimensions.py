#!/usr/bin/env python3

from lxml import etree
import json
import re
import sys
import os
import hashlib
import boto3
import gzip

pathpattern = re.compile('^image/(W[A-Z0-9]+)-([A-Z0-9]+)--([A-Z0-9]+)__\d+\.([a-zA-Z0-9]+)$')

outdir = 'output/'
s3bucketName = 'archive.tbrc.org'
s3client = boto3.resource('s3')
s3bucket = s3client.Bucket(s3bucketName)

ns = {'premis': 'info:lc/xmlns/premis-v2',
      'mix': 'http://www.loc.gov/mix/v20',
      'mets': 'http://www.loc.gov/METS/'}

def add_info_to_struct(path, width, height, struct):
    m = pathpattern.match(path)
    if not m:
        print('cannot parse path string "'+path+'"', file=sys.stderr)
        return
    filename = m.group(3)+'.'+m.group(4)
    struct.append({'filename': filename, 'width': width, 'height': height})

def get_list_from_file(filename):
    global ns
    doc = etree.ElementTree(file=filename)
    struct = []
    for node in doc.findall('/mets:amdSec/mets:techMD/mets:mdWrap[@MDTYPE="PREMIS:OBJECT"]/mets:xmlData/premis:object', ns):
        path = node.findall('premis:objectIdentifier/premis:objectIdentifierValue', ns)[0].text
        characteristics_nodes = node.findall("premis:objectCharacteristics/premis:objectCharacteristicsExtension/mix:mix/mix:BasicImageInformation/mix:BasicImageCharacteristics", ns)
        if (len(characteristics_nodes) < 1):
            continue
        characteristics_node = characteristics_nodes[0]
        width=int(characteristics_node.findall('mix:imageWidth', ns)[0].text)
        height=int(characteristics_node.findall('mix:imageHeight', ns)[0].text)
        add_info_to_struct(path, width, height, struct)
    return struct

def get_outfile_name(dirname):
    lastdir = dirname.split('/')[-1]
    workid = lastdir.split('-')[0]
    md5 = hashlib.md5(workid.encode('utf-8')).hexdigest()[:2]
    return outdir+md5+'_'+workid+'_'+lastdir+'_dimensions.json'

def get_s3_key(dirname):
    lastdir = dirname.split('/')[-1]
    workid = lastdir.split('-')[0]
    md5 = hashlib.md5(workid.encode('utf-8')).hexdigest()[:2]
    return 'Works/'+md5+'/'+workid+'/images/'+lastdir+'/dimensions.json'

def build_lists_from_dir(dirname):
    for root, batchdirnames, _ in os.walk(dirname):
        if root.count(os.path.sep) == 2: # yeark...
            key = get_s3_key(root)
            list = get_list_from_file(root+'/descriptor.xml')
            jsonstr = json.dumps(list)
            # with open(get_outfile_name(root), 'w') as outfile:
            #     json.dump(list, outfile)
            json_data = bytes(jsonstr, 'utf-8')
            gzip_data = gzip.compress(json_data)
            print("uploading %s" % key)
            s3bucket.put_object(Key=key, Body=gzip_data, ContentType='application/json', ContentEncoding='gzip')

#struct = get_list_from_file("METS-descriptors-W22084-22703-22704/batchW22084-1/W22084-0886/descriptor.xml")
#print(struct)
build_lists_from_dir("METS-descriptors-W22084-22703-22704")

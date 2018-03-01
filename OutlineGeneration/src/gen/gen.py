'''
Created on Feb 28, 2018

@author: jsk
'''
import sys
from lxml import etree
import codecs
outLineURI = "https://www.tbrc.org/public?module=outline&query=outlines"
'''
get_attr_text_from_file

 Parses an xml document for nodes in Path.
 extracts the value of attrName and the 
 node's text
 
'''
def get_attr_text_from_file(args,attrName,path):
    doc = etree.parse(args)
    _path = path+'[@'+attrName+']'
    work_nodes = doc.xpath(_path)
    return [ get_value(aNode,attrName) for aNode in work_nodes ]
#     for aNode in work_nodes:
#         try:
#            struct.append(get_value(aNode,attrName))
#             struct.append((workId,outline))
#         except:
#             # TODO: handle node without work. Print RID, text?
#             pass

def get_value(node,attrName):
    return node.xpath("@"+attrName)[0],node.text
   
def write_list( outFilePath, vals):
    with codecs.open(outFilePath,  'w', encoding="utf-8") as out:
#        sigh. no unicode in csv
#         wr = _csv.writer(out)
#         wr.writerow(['workName','outlineText'])
#         [ wr.writerow([aVal[0],aVal[1]]) for aVal in vals ]
        out.write('{0},{1}\n'.format('workName','outlineText'))
        _ =  [ out.write('{0},"{1}"\n'.format(aVal[0],aVal[1].strip())) \
               for aVal in vals ]

def main(args):
    inFilePath = args[0]
    outFilePath = args[1]
    
    outlines = get_attr_text_from_file(inFilePath,'work','/outlines/outline')
    write_list(outFilePath,outlines)
    



if __name__ == '__main__':
        main(sys.argv[1:])
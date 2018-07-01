"""
Created on Feb 28, 2018

@author: jsk

@summary: Library to parse input xml
"""

from lxml import etree


class OutlineReader:

    def get_attr_text(self, doc, attrName, path):
        """Returns a list of tuples of: the values of attrName, the text
        of the nodes which contain the attribute attrName
         @param doc: XML document
         @param attrName: attribute whose value we want
         @param path: XPath expression locating the node which contains
         attrName
     """
        _path = path+'[@'+attrName+']'
        work_nodes = doc.xpath(_path)
        return [self.get_value(aNode, attrName) for aNode in work_nodes]
    #     for aNode in work_nodes:
    #         try:
    #            struct.append(get_value(aNode,attrName))
    #             struct.append((workId,outline))
    #         except:
    #             # TODO: handle node without work. Print RID, text?
    #             pass

    @staticmethod
    def get_value(node, attrName):
        """
        @summary Extract the given attributes value and the node's text
        @param node: XML node containing attribute attrName
        @param attrName: which attribute to extract the value from
        """
        return node.xpath("@"+attrName)[0], node.text

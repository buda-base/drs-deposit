"""
Created on Feb 28, 2018

@author: jsk

@summary: Library to parse input xml
"""


class OutlineReader:

    def get_attr_text(self, doc, attr_name, path):
        """Returns a list of tuples of: the values of attrName, the text
        of the nodes which contain the attribute attrName
         @param doc: XML document
         @param attr_name: attribute whose value we want
         @param path: XPath expression locating the node which contains
         attrName
     """
        _path = path + '[@' + attr_name + ']'
        work_nodes = doc.xpath(_path)
        return [self.get_value(aNode, attr_name) for aNode in work_nodes]

    #     for aNode in work_nodes:
    #         try:
    #            struct.append(get_value(aNode,attrName))
    #             struct.append((workId,outline))
    #         except:
    #             # TODO: handle node without work. Print RID, text?
    #             pass

    @staticmethod
    def get_value(node, attr_name):
        """
        @summary Extract the given attributes value and the node's text
        @param node: XML node containing attribute attrName
        @param attr_name: which attribute to extract the value from
        """
        return node.xpath("@" + attr_name)[0], node.text

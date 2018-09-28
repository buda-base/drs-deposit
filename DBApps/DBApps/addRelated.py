#!/usr/bin/env python3

"""
Entry point for getting related files.
@author: jimk
@date 2018-IX-27
A typical input was cut -f1 -d'|' Github://drs-deposit/output/outlines/

"""
from DBApps.relatedAdder import AddRelatedParser, RelatedAdder


def AddRelated():
    """
    Entry point for getting Related files, either outlines or print masters
    :return:
    """
    arp = AddRelatedParser(
        description="Adds list of works to either outlines or printmasters",
        usage=" sourceFile: list of workNames")

    addArgs = arp.parsedArgs

    ar = RelatedAdder(addArgs)
    ar.Add(sproc=f'Add{ar.TypeString}', sourceFile=addArgs.sourceFile)


if __name__ == "__main__":
    AddRelated()

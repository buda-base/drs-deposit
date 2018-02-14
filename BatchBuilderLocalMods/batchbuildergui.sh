#!/bin/bash

BB_HOME=`dirname "$0"`
export BB_HOME

java -Dlog4j.configuration=intentional/fake/path -cp "$BB_HOME:$BB_HOME/lib/*:$BB_HOME/fits/lib/*" -Xms128m -Xmx1024m edu.harvard.hul.ois.bb.gui.App

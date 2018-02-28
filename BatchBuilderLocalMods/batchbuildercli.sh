#!/bin/bash

BB_HOME=`dirname "$0"`
export BB_HOME

# concatenate args and use eval/exec to preserve spaces in paths, options and args
args=""
for arg in "$@" ; do
args="$args \"$arg\""
done

cmd="java -Dlog4j.configuration=intentional/fake/path -cp \"$BB_HOME:$BB_HOME/lib/*:$BB_HOME/fits/lib/*\" -Xms512m -Xmx2048m edu.harvard.hul.ois.bb.cli.BBCli $args"

eval "exec $cmd"


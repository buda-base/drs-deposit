#!/usr/bin/env bash
#parallelising runDRS inputs
# with the same input as before filename[1-n] ideas as follows
# ls $* | parallel runAny.sh makeOneDrs.sh {}
runAny.sh makeOneDrs.sh $*

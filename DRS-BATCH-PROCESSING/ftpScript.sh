#!/bin/bash
[ -f something ] || touch something
[ -f something ] && cp something somewhereElse


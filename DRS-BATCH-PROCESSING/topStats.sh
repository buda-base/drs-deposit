#!/bin/bash

 top -stats cpu,mem,time,pid,ppid,state,command,pgrp -s 3 -U jimk -o cpu -O mem  -F -n 25  $*



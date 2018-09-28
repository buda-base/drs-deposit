#!/usr/bin/env
# Source, don't call
#
# Validates required inputs exist

# MAKEDRS is the command executable

unset makeOneErrors

[ -x "${MAKEDRS}" ]            || { makeOneErrors=$(printf "MAKEDRS \'${MAKEDRS}\' is not executable") ;}
[ -d  "${PROJECT_HOME}" ]      || { makeOneErrors="$makeOneErrors \nPROJECT_HOME '${PROJECT_HOME}' is not a directory";}
[ -d  "${WORKS_SOURCE_HOME}" ] || { makeOneErrors="$makeOneErrors \nWORKS_SOURCE_HOME '${WORKS_SOURCE_HOME}' is not a directory";}
[ -d  "${BB_SOURCE}" ]           || { makeOneErrors="$makeOneErrors \BB_SOURCE '${BB_SOURCE}' is not a directory";}

[ -z "${makeOneErrors}" ] || { echo -ne "${ME}:error:\n${makeOneErrors}" ; exit 1 ; }

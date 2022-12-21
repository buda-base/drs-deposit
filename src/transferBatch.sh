#!/usr/bin/env bash
# copy batches from bodhi to local current directory
batchList=${1?"List of batch names required"}
if [[ ! -f $batchList ]] ; then
    echo "source fille $batchList not found."
    exit 1
fi

runStart=$(date  +%H-%M-%S)
cat $batchList | parallel -j 4 --joblog ${runStart}.fromBodhi.log 'rsync -avz   bodhi.local::drsbuilds/prod/batchBuilds/{}/ /Volumes/DRS_Staging/DRS/prod/batchBuildsFromBodhi/{} | tee -a {%}.get.log'

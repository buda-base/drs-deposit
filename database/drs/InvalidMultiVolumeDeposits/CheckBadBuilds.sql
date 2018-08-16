select * from BatchBuilds where buildPathId in (66405, 66406);

#
# INSERT INTO `drs`.`BatchBuilds`
# (
# `BuildDate`,
# `Result`,
# `buildPathId`)
# VALUES
# (CURRENT_TIMESTAMP(),"success",66406);
#
# INSERT INTO `drs`.`Volumes`
# (`workId`,
# `label`,
# `batchBuildId`,
# `builtFileSize`,
# `builtFileCount`,
# `Queued`)
# VALUES
# (1,
# 'TestDeletion83934',
# 83934,
# 4242,
# 42,
# b'1');

INSERT INTO `drs`.`DRS`
(
`IngestDate`,
`objectid`,
`DRSdir`,
`objectUrn`,
`filesCount`,
`size`,
`OSN`)
VALUES
(
CURRENT_TIME(),
4225,
'Harkabeeparolyn-1n',
'urn42:4225',
22,
4243,
'TestDeletion83934');

#
# update Volumes set label = 'TestDeletion83933' where volumeId = 32521;
# select * from Volumes where  create_time > '2018-08-01';
#
select * from DRS order by create_time desc limit 4;

select * from Volumes join DRS using(volumeId) where volumeId =  32521;

update DRS set OSN = (select label from Volumes where volumeId = 32521) where objectid = 4322;


# Bad objects volume Queued volume = false
 update Volumes set Queued =False where volumeId in (select volumeId from DRS where objectid in (4225,4322));


# find and delete build paths
# modify this query to delete instead of select *
select bp.* from BuildPaths bp where buildPathId in
                                     (
    select buildPathId from BatchBuilds
join Volumes using(batchBuildId)
join DRS using (volumeId)
where objectid in (4225,4322));

/*delete from BuildPaths  where buildPathId in
                                     (
    select buildPathId from BatchBuilds
join Volumes using(batchBuildId)
join DRS using (volumeId)
where objectid in (4225,4322));
*/
# validate buildPathId is null in this query after above delete run
select * from BatchBuilds where batchBuildId in (select batchBuildId from Volumes join DRS d using (volumeId)
                                                       where d.objectid in (4225,4322));
# modify this query to delete instead of select *
select * from BatchBuilds     where batchBuildId in ( select batchBuildId from  Volumes v  join DRS using (volumeId)
                                                         where objectid in (4225,4322)
                                                         );
# delete from BatchBuilds     where batchBuildId in ( select batchBuildId from  Volumes v  join DRS using (volumeId)
#                                                         where objectid in (4225,4322)
#                                                         );

select v.* from Volumes v  join DRS using (volumeId)
                                                        where objectid in (4225,4322);

# and last
# delete from DRS  where objectid in (4225,4322);

select * from badObjectsWithDates where oid in (
    select oid from objdel2296
union select oid from objdel2972
union select oid from objdel4976
union select oid from objdel4985
union select oid from objdel7200
union select oid from objdel7233
    );

select * from Volumes v
join BatchBuilds BB on v.batchBuildId = BB.batchBuildId
join BuildPaths Path on BB.buildPathId = Path.buildPathId
join badBatchesBuiltFullPath bbfp on bbfp.BuildPath = Path.BuildPath;

select BuildPath from BuildPaths where BuildPath like '%batchBuild%';
-- how many bad batch builds have batchBuild table entries
select count(*) from badBatchesBuiltFullPath bfp
                       join BuildPaths bp on bfp.BuildPath = bp.BuildPath
                      join BatchBuilds bb on bb.batchBuildId = bp.buildPathId;
-- how many volumes are in the bad batches (use work to separate)

-- how many bad objects?
select count(*) from badObjectsWithDates;

-- how many objects in the query are not in bad objects?

-- and how many objects in bad objects are not in the query?
select * from badObjectsWithDates bowd left outer join DRS d on d.objectid = bowd.oid where d.objectid is null;
select distinct date(IngestDate) from DRS

select count(*) from Volumes v join Works w using(workId) join badWorksBuilt bwb on bwb.Work = w.WorkName
join DRS d using(volumeId);
;

select w.WorkName, v.label, v.builtFileCount, v.builtFileSize, bb.BuildDate, bb.Result, bp.BuildPath from Volumes v
                join allBatchBuiltVols abb on v.label = abb.label
                left join BatchBuilds bb using(batchBuildId)
                join BuildPaths bp using(buildPathId)
                join Works w using(workId)
where batchBuildId is not null
and bp.BuildPath like '%batchBuilds%';


select v.label from Volumes v
                      join allBatchBuiltVols abb on v.label = abb.label
                left join BatchBuilds bb using(batchBuildId)
                join Works w using(workId)
where batchBuildId is null;

select v.* from Volumes v join BatchBuilds bb using(batchBuildId) where bb.update_time > current_date;

call WeeklyStatus();
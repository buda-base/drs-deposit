select V.*, D.DRSdir  from DRS D
inner join  Volumes V on D.volumeId = V.volumeId
where V.batchBuildId is null ;

select distinct label  from Volumes where Queued = 1 and batchBuildId is null and builtFileSize is null order by volumeId asc;

select * from Outlines ; 

select  *  from Volumes V 
inner join DRS D on D.OSN = V.label
where D.OSN in ('W30498-I1CZ4883',' W1KG13126-I1KG13276') ;

select * from BuildPaths where BuildPath like 'batchW30498%' ; 

select label from Volumes v
left join Outlines o on o.volumeId = v.volumeId
left join PrintMasters p on p.volumeId = v.volumeId
where o.volumeI`vols-no-depo``vols-no-depo`d is null 
and p.volumeId is null
and batchBuildId is  null and Queued = 1;

select * from Volumes v
inner join BatchBuilds bb on v.batchBuildId = bb.batchBuildId
inner join BuildPaths bp on bp.buildPathId	= bb.buildPathId
inner join deposited_vol_data dvd
on locate(dvd.batch_dir, bp.BuildPath) > 0 ;

select * from DRS where DRSdir =AddDRS 'batchW00EGS1016236-1-2e' ;--  = 'W00EGS1016236-I00JW501109';


set @target = '/Volumes/DRS_Staging/DRS/prod/batchBuilds/batchW1KG13617-2-64';
select  buildPathId from BuildPaths where BuildPath = @target ;
select batchBuildId from BatchBuilds where buildPathId = (select buildPathId from BuildPaths where BuildPath = @target);

set @bpId = (select buildPathId from BuildPaths where BuildPath = @target);
set @bbId = ( select batchBuildId from BatchBuilds where buildPathId = (select buildPathId from BuildPaths where buildPathId = @bpId));

select @bpId, @bbId, label, Queued, batchBuildId from Volumes where batchBuildId = @bbId ;

-- select count(*) from Volumes where Queued = 1; 
select count(*) from Volumes where batchBuildId is not null ;

select d.OSN, d.DRSDir, d.filesCount, d.size, d.IngestDate from DRS d
-- inner join Volumes v on v.label = d.OSN 
inner join BuildPaths bp on locate(d.DRSDir, bp.BuildPath) > 0;


select distinct d.DRSdir from DRS d left join BuildPaths bp on d.DRSdir = bp.build_dir
where bp.build_dir is null
and d.DRSDir like 'batchW%';

select count(distinct batchBuildId)  from BatchBuilds  where create_time > '2020-08-31' order by create_timeDeleteBatchBuild desc;

select * from BuildPaths where buildPath like '%22704-3-66%';

select * from BuildPaths  where update_time > '2020-11-23';

select * from Volumes v inner join Works w on w.workId = v.workId
where workName in (
'W00EGS1016286',
'W00EGS1016703',
'W00EGS1016899',
'W00JW501203',
'W00KG03612',
'W1022',
'W10736',
'W19229',
'W1934',
'W19341');


select v.label, v.update_time  from `vols-no-depo` n  
inner join Volumes v on v.label = n.label 
inner join BatchBuilds bb on v.batchBuildid = bb.batchBuildId
inner join BuildPaths bp on bp.buildPathId = bb.buildPathId 
where bp.buildPath like '%9-3-d2';

select v.* from Volumes v  
 where label like 'W00EGS1016299%' ;

-- get me buildpaths which are deposited, but havbe batchBuildId null
-- get me deposited volumes with batch builds without batchbuildid
select bp.buildPathId, bb.batchBuildId  from BatchBuilds bb 
inner join BuildPaths bp on bp.buildPathId = bb.buildPathId
where (select substring_index(bp.buildPath,'/',-1)
 in (
select distinct d.DRSdir  from Volumes v 
inner join DRS d on d.osn = v.label
where v.batchBuildId is null )) ;


-- BUILD PATH ID 59819,94003,94005
-- BATCHBUILD ID 67987,102121,102123
select * from Volumes v where batchBuildId in (  67987,102121,102123);


select * from BuildPaths where buildPathId in ( 67987,102121,102123);


explain select bp.buildPathId, bb.batchBuildId  from BatchBuilds bb 
inner join BuildPaths bp on bp.buildPathId = bb.buildPathId
where (select substring_index(bp.buildPath,'/',-1)
 in (
select distinct d.DRSdir  from Volumes v 
inner join DRS d on d.osn = v.label
where v.batchBuildId is null )) ;


select substring_index('/11/22/33/44','/',-1);

select distinct d.drsdir from Volumes v 
inner join DRS d on d.osn = v.label
where v.batchBuildId is null;

-- get the DRS deposit records for where theres a DRS but no batchbuild
select * from DRS d2 where d2.DRSdir in (
select substring_index(bp.BuildPath,'/',-1)  from BuildPaths bp  where substring_index(bp.BuildPath,'/',-1) in (
select distinct d.drsdir from Volumes v 
inner join DRS d on d.osn = v.label
where v.batchBuildId is null)) ;

-- get the volumes for the above
select distinct d2.volumeId, d2.osn, d2.DRSDir from DRS d2 where d2.DRSdir in (
select substring_index(bp.BuildPath,'/',-1)  from BuildPaths bp  where substring_index(bp.BuildPath,'/',-1) in (
select distinct d.drsdir from Volumes v 
inner join DRS d on d.osn = v.label
where v.batchBuildId is null));

-- 16 sec
select d4.osn,d4.DRSDir, d4.IngestDate,d4.filesCount,d4.size from Volumes v3 
inner join DRS d4 on d4.volumeId = v3.volumeId
where v3.volumeId in 
(select volumeId from DRS d2 where d2.DRSdir in (
select substring_index(bp.BuildPath,'/',-1)  from BuildPaths bp  where substring_index(bp.BuildPath,'/',-1) in (
select distinct d.drsdir from Volumes v 
inner join DRS d on d.osn = v.label
where v.batchBuildId is null))) and v3.batchBuildId is null;


-- and update vols-no-depo
select `vols-no-depo`.`label`,
    `vols-no-depo`.`batch_dir`,
    `vols-no-depo`.`import_date`,
    `vols-no-depo`.`file_count`,
    `vols-no-depo`.`total_size`;
    
    
INSERT INTO `drs`.`vols-no-depo`
(
`label`,
`batch_dir`,
`import_date`,
`file_count`,
`total_size`)
select d4.osn,d4.DRSDir, d4.IngestDate,d4.filesCount,d4.size  from Volumes v3 
inner join DRS d4 on d4.volumeId = v3.volumeId
where v3.volumeId in 
(select volumeId from DRS d2 where d2.DRSdir in (
select substring_index(bp.BuildPath,'/',-1)  from BuildPaths bp  where substring_index(bp.BuildPath,'/',-1) in (
select distinct d.drsdir from Volumes v 
inner join DRS d on d.osn = v.label
where v.batchBuildId is null))) and v3.batchBuildId is null;

-- and finally, update
call UpdateBatchBuildsFromBDRCcum;


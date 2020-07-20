-- call GetReadyVolumesTest(34);
-- 
-- SHOW ENGINE INNODB STATUS;
-- 
select  count( r.workId ) from Works r
                             inner join Volumes v on r.workId = v.workId  where not v.Queued ;

select * from Volumes v where batchBuildId IS NULL  and builtFileSize is not null ;
-- TODO: Get5 the batchBuildIDs for these
select  w.workName, v.label, v.Queued  from  Works w inner join Volumes v on v.workId = w.workId
where v.batchBuildId IS NULL  and v.builtFileSize is null and w.HOLLIS is not null ;

-- get workNames
select count(  w.workId) as volumecount,  count(distinct w.workId) as workCount  from  Works w inner join Volumes v on v.workId = w.workId
where v.batchBuildId IS NULL  and v.builtFileSize is null and w.HOLLIS is not null ;

select v.label, v.update_time from Works w inner join Volumes v on v.workId = w.workId
where v.batchBuildId IS NULL  and v.builtFileSize is null and w.HOLLIS is not null ;

select max(v.update_time), min(v.update_time)  from Works w inner join Volumes v on v.workId = w.workId
where v.batchBuildId IS NULL  and v.builtFileSize is null and w.HOLLIS is not null ;


drop table if exists tWork ;
call GetReadyVolumes(10);

select * from tWork;


select * from BatchBuilds order by create_time desc;

call SetVolumeUnbuilt('W1KG13126-I1KG13286');
select * from BuildPaths where BuildPath like '%batchW1KG13126-4%';
select * from Volumes where label like 'W1KG13126-I1KG132%' ; 

select * from DRS where volumeId = (select volumeId from Volumes where label = 'W1KG13126-I1KG13275');

select * from DRS where DRSDir in 
("batchW00KG02762-1n",
"batchW00KG02762n",
"batchW00KG0541-1n",
"batchW00KG0541n",
"batchW1KG13126-3-65",
"batchW1KG13126-3-92",
"batchW1KG13126-4-17",
"batchW1KG13126-4-4e",
"batchW1KG13126-5-c1",
"batchW1KG13126-6-5d",
"batchW22084-1-23",
"batchW22084-2-84",
"batchW22084-2-85",
"batchW22084-3-3f",
"batchW22084-3-ed",
"batchW22084-4-e3",
"batchW22084-4-e9",
"batchW22084-5-5f",
"batchW22110-1-7b",
"batchW22110-1-ea",
"batchW22245-1-93",
"batchW22245-1-b3",
"batchW23202-1-27",
"batchW23202-1-34",
"batchW23229-1-28",
"batchW23229-1-eb",
"batchW23543-1-5d",
"batchW23543-1n",
"batchW23606-1-07",
"batchW23606-1-a9",
"batchW23621-1-10",
"batchW23621-1-2d",
"batchW23682-1-a9",
"batchW23682-1-e9",
"batchW23843-1-b1",
"batchW23843-1-eb",
"batchW23930-1-56",
"batchW23930-1-99",
"batchW27551-1-20",
"batchW27551-1-ef",
"batchW27552-1-ba",
"batchW27552-1-bb");


select * from BuildPaths where BuildPath = ''
or BuildPath like "%batchW00KG02762-1n"
or BuildPath like "%batchW00KG02762n"
or BuildPath like "%batchW00KG0541-1n"
or BuildPath like "%batchW00KG0541n"
or BuildPath like "%batchW1KG13126-3-65"
or BuildPath like "%batchW1KG13126-3-92"
or BuildPath like "%batchW1KG13126-4-17"
or BuildPath like "%batchW1KG13126-4-4e"
or BuildPath like "%batchW1KG13126-5-c1"
or BuildPath like "%batchW1KG13126-6-5d"
or BuildPath like "%batchW22084-1-23"
or BuildPath like "%batchW22084-2-84"
or BuildPath like "%batchW22084-2-85"
or BuildPath like "%batchW22084-3-3f"
or BuildPath like "%batchW22084-3-ed"
or BuildPath like "%batchW22084-4-e3"
or BuildPath like "%batchW22084-4-e9"
or BuildPath like "%batchW22084-5-5f"
or BuildPath like "%batchW22110-1-7b"
or BuildPath like "%batchW22110-1-ea"
or BuildPath like "%batchW22245-1-93"
or BuildPath like "%batchW22245-1-b3"
or BuildPath like "%batchW23202-1-27"
or BuildPath like "%batchW23202-1-34"
or BuildPath like "%batchW23229-1-28"
or BuildPath like "%batchW23229-1-eb"
or BuildPath like "%batchW23543-1-5d"
or BuildPath like "%batchW23543-1n"
or BuildPath like "%batchW23606-1-07"
or BuildPath like "%batchW23606-1-a9"
or BuildPath like "%batchW23621-1-10"
or BuildPath like "%batchW23621-1-2d"
or BuildPath like "%batchW23682-1-a9"
or BuildPath like "%batchW23682-1-e9"
or BuildPath like "%batchW23843-1-b1"
or BuildPath like "%batchW23843-1-eb"
or BuildPath like "%batchW23930-1-56"
or BuildPath like "%batchW23930-1-99"
or BuildPath like "%batchW27551-1-20"
or BuildPath like "%batchW27551-1-ef"
or BuildPath like "%batchW27552-1-ba"
or BuildPath like "%batchW27552-1-bb";


select max(IngestDate) from DRS ; 


-- this confirms that nothing with these batch builds is deposited
select count(*) from DRS where OSN in (
select label from Volumes V where batchBuildId  in
(select batchBuildId from BatchBuilds BB
inner join BuildPaths BP on BB.buildPathId = BP.buildPathId
 where 
BuildPath like "%batchW1KG13126-3-65"
or BuildPath like "%batchW1KG13126-3-92"
or BuildPath like "%batchW1KG13126-4-4e"
or BuildPath like "%batchW1KG13126-6-5d"
or BuildPath like "%batchW22084-1-23"
or BuildPath like "%batchW22084-3-3f"
or BuildPath like "%batchW22084-4-e9"
or BuildPath like "%batchW22110-1-7b"
or BuildPath like "%batchW22110-1-ea"
or BuildPath like "%batchW23543-1-5d"
or BuildPath like "%batchW23543-1n"));

select * from DRS where OSN like 'W22084-%AddDRS' ;

select distinct DATE(IngestDate) from DRS;

select * from DRS where DATE(IngestDate) = '2018-08-11';
-- now get the undeposited volumes from the batch builds

create temporary table tVols as select v1.label from Volumes v1 where v1.batchBuildId  in
(select batchBuildId from BatchBuilds BB
inner join BuildPaths BP on BB.buildPathId = BP.buildPathId
 where 
BuildPath like "%batchW1KG13126-3-65"
or BuildPath like "%batchW1KG13126-3-92"
or BuildPath like "%batchW1KG13126-4-4e"
or BuildPath like "%batchW1KG13126-6-5d"
or BuildPath like "%batchW22084-1-23"
or BuildPath like "%batchW22084-3-3f"
or BuildPath like "%batchW22084-4-e9"
or BuildPath like "%batchW22110-1-7b"
or BuildPath like "%batchW22110-1-ea"
or BuildPath like "%batchW23543-1-5d"
or BuildPath like "%batchW23543-1n")
and v1.label not in (select OSN from DRS);

update Volumes as vt set vt.Queued = 0, vt.batchBuildId = null where vt.label in (select label from tVols);

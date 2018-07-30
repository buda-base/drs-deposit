-- Get me the build paths, volumes and counts which have multiple volumes,
-- and were built by the bogus program (like '%batchBuilds%')
SELECT distinct BuildPath  , v.label, v.builtFileCount 
FROM drs.BatchBuilds bb 
join BuildPaths bp using(buildPathId) 
join Volumes v using (batchBuildId)
where bp.buildPathId in (
	select buildPathId from (
		SELECT  bb2.buildPathId, count(v3.label) as vols 
		FROM drs.BatchBuilds bb2 
		join BuildPaths bp2 using(buildPathId) 
		join Volumes v3 using (batchBuildId)
		where bb2.Result = "success"
		and bp2.BuildPath like '%batchBuilds%'
        group by bb2.BuildPathId) vv
        where vv.vols > 1
        ) ;
;

-- Get me the volume ids of the above.
-- and were built by the bogus program (like '%batchBuilds%')
-- AND have not been deposited.
SELECT distinct BuildPath  , v.volumeId -- v.label, ,v.builtFileCount 
FROM drs.BatchBuilds bb 
join BuildPaths bp using(buildPathId) 
join Volumes v using (batchBuildId)
left join DRS using(volumeId)
where bp.buildPathId in (
	select buildPathId from (
		SELECT  bb2.buildPathId, count(v3.label) as vols 
		FROM drs.BatchBuilds bb2 
		join BuildPaths bp2 using(buildPathId) 
		join Volumes v3 using (batchBuildId)
		where bb2.Result = "success"
		and bp2.BuildPath like '%batchBuilds%'
        group by bb2.BuildPathId) vv
        where vv.vols > 1
        ) 
and DRSId is null ;
;

select database();
-- now get the deposit records for the same
select count(distinct DRSDir) from DRS d
join Volumes v using(volumeId) 
join BatchBuilds b using(batchBuildId)
where b.buildPathId in (
	select buildPathId from (
		SELECT  bb2.buildPathId, count(v3.label) as vols 
		FROM drs.BatchBuilds bb2 
		join BuildPaths bp2 using(buildPathId) 
		join Volumes v3 using (batchBuildId)
		where bb2.Result = "success"
		and bp2.BuildPath like '%batchBuilds%'
        group by bb2.BuildPathId) vv
        where vv.vols > 1
        ) ;

-- NOW, Get me only the buildpath Ids. These are the 
-- buildPaths which have not been deposited, and need to be wiped out.
-- the volume ids of the above.
-- and were built by the bogus program (like '%batchBuilds%')
-- AND have not been deposited.
SELECT distinct BuildPath --  , v.volumeId -- v.label, ,v.builtFileCount 
FROM drs.BatchBuilds bb 
join BuildPaths bp using(buildPathId) 
join Volumes v using (batchBuildId)
left join DRS using(volumeId)
where bp.buildPathId in (
	select buildPathId from (
		SELECT  bb2.buildPathId, count(v3.label) as vols 
		FROM drs.BatchBuilds bb2 
		join BuildPaths bp2 using(buildPathId) 
		join Volumes v3 using (batchBuildId)
		where bb2.Result = "success"
		and bp2.BuildPath like '%batchBuilds%'
        group by bb2.BuildPathId) vv
        where vv.vols > 1
        ) 
and DRSId is null ;
;


SELECT buildPathId, WorkName, v.label, v.builtFileCount -- (v.label) as vols  -- BuildDate,BuildPath, v.label, v.builtFileCount 
FROM drs.BatchBuilds bb 
join BuildPaths bp using(buildPathId) 
join Volumes v using (batchBuildId)
join Works w using(workId)
where bb.Result = "success"
and bp.BuildPath like '%batchBuilds%'
order by buildPathId asc, v.label asc;


/*
SELECT  BuildPath, WorkName, count(v.label) as vols  -- BuildDate,BuildPath, v.label, v.builtFileCount 
FROM drs.BatchBuilds bb 
join BuildPaths bp using(buildPathId) 
join Volumes v using (batchBuildId)
join Works w using(workId)
where bb.Result = "success"
and bp.BuildPath like '%batchBuilds%'
group by batchBuildId
	having vols = 1;
--	having vols > 1;
*/
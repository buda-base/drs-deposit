-- debug update work status count


select distinct workId from Volumes where  not Queued limit 3;

-- Volumes sent for batch, but not batched
select count(distinct workId) from Volumes v
left join BatchBuilds using (batchBuildId)
where v.Queued and v.batchBuildId is  null;

-- Count Volumes sent for batch and built, by Result
select bb.Result,count(bb.Result) from Volumes v
left join BatchBuilds bb using (batchBuildId)
where v.Queued and v.batchBuildId is not null
group by bb.Result;

-- works sent to batch and batched (batchBuildId is not null)
select count(distinct v.workId)BatchedCompleteWorks from Volumes v
left join BatchBuilds bb using (batchBuildId)
where v.Queued and v.batchBuildId is not null;	

-- works sent to batch and batched (batchBuildId is  null)
select count(distinct v.workId)BatchedPartialWorks from Volumes v
left join BatchBuilds bb using (batchBuildId)
where v.Queued and v.batchBuildId is null;


-- Volumes DRSd

-- queued not built
select count(distinct volumeId) NumberWorksPartialInDRS from Volumes v
-- inner join Works w using(workId) 
left join DRS d using(volumeId)
	where DRSid is not null;


-- try to get the number of volumes in a work, and the number of volumes 
-- which have been deposited

	select count(*)
    -- (select count(volumeId) from Volumes where workId = w.workId ) as workVolumes
    from Works as w ; 
    
    select count(volumeId) from volumes
    select count(*) from Works w;
    select count(distinct WorkName) from Works ;
    
    
`NumberVolumesBatchBuilt` = 
(select count(1) from Volumes v
inner join Volumes v using(volmeId) 
inner join Works w using(workId) 
left join DRS d using(volumeId)
	where w.workId = workId
    and bb.QueuedDate is not null
    and bb.BuildDate is not null
    and bb.TransferQueuedDate is null
    and bb.TransferCompleteDate is null
    and d.DRSId is null)
    ,
    
`NumberVolumesUploadQueued` =     
(select count(1) from BatchBuilds bb 
inner join Volumes v using(volumeId) 
inner join Works w using(workId) 
left join DRS d using(volumeId)
	where w.workId = workId
    and bb.QueuedDate is not null
    and bb.BuildDate is not null
    and bb.TransferQueuedDate is not null
    and bb.TransferCompleteDate is null
    and d.DRSId is null)
    ,

`NumberVolumesUploaded` =
(select count(1) from BatchBuilds bb 
inner join Volumes v using(volumeId) 
inner join Works w using(workId) 
left join DRS d using(volumeId)
	where w.workId = workId
    and bb.QueuedDate is not null
    and bb.BuildDate is not null
    and bb.TransferQueuedDate is not null
    and bb.TransferCompleteDate is Not null
    and d.DRSId is null
    )
    ,
`NumberVolumesDeposited` =
(select count(1) from Works w
inner join Volumes v using (workId)
left join DRS using (volumeId)
where 
v.workId = workId
and drsId is not null
)
;


-- Get the count of works in volumes and works in DRS. This might be flaky
	select workId, count(vv.volumeId) wvct, count(dd.drsId)dvct  from Volumes vv join DRS dd using(volumeId) join Works w using(workId)  group by w.workId ; 
   --   ; having wvct <> dvct ; 
    
    -- Get the count of works in volumes and works in DRS. This might be flaky
	select workId, count(vv.volumeId) wvct from Volumes vv left join DRS dd using(volumeId) join Works w using(workId) 
    where dd.DRSDir is null
    group by w.workId ; 
   --   ; having wvct <> dvct ; 
    
    	select workId, count(vv.volumeId) wvct from Volumes vv left join DRS dd using(volumeId) join Works w using(workId) 
    where dd.DRSDir is not null
    group by w.workId ; 
    
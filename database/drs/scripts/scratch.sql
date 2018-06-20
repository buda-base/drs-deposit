-- call AddWork('WorkPartial2','H12345_2');
call AddVolume('WorkPartial4','WP42-Vol1');
select * from Volumes where label = 'WP42-Vol1';

select  w.workId, w.WorkName, w.HOLLIS, v.volumeId vVol, v.label, d.volumeId dVol, d.DRSdir , d.create_time from Works w inner join Volumes v using(workId) left join DRS d using (volumeId)  where WorkName like '%art%' and d.DRSdir is not null;
select  distinct w.WorkName, w.HOLLIS from Works w inner join Volumes v using(workId) left join DRS d using (volumeId)  where WorkName like '%art%' and d.DRSdir is not null;

-- this gets you works where any one has been uploaded
select  w.WorkName, w.HOLLIS , v.volumeId, v.label, d.DRSdir from  Works w
  join Volumes v using(workId)
  join DRS d using (volumeId)
  where  -- WorkName like '%art%' and
        exists  (select volumeId from DRS d where d.volumeId = v.volumeId)
and d.DRSdir not like '%1';

-- this gets you any where any volume has NOT been uploaded
select  w.WorkName, w.HOLLIS , v.volumeId, v.label from  Works w
  inner join Volumes v using(workId)
  where  -- WorkName like '%art%' and
        not  exists  (select volumeId from DRS d where d.volumeId = v.volumeId);

-- what gets you the one where all have been uploaded?
select  w.WorkName, w.HOLLIS , v.volumeId, v.label, (select count(volumeId) from Volumes v where v.workId = w.workId) vw  from  Works w
  join Volumes v using(workId)
  left join DRS d using (volumeId)
--   where WorkName like '%art%' ;
       having (select count(volumeId) from DRS d where d.volumeId = v.volumeId);


/*********     TEST SECTION  **************/
select (select count(1) from Volumes v where label like 'WP1%') = (select count(1) from Volumes v where label like 'WP42%') ;

-- try counting first
select count(volumeId) from Volumes where label like 'WP%';
select count(d.volumeId) from DRS d, Volumes v where v.label like 'WP%' and d.volumeId = v.volumeId ;

/*********     END TEST SECTION  **************/
select count(workId) from Works w inner join Volumes v using (workId) left join DRS d using (volumeId) where  exists  (select volumeId from DRS d where d.volumeId = v.volumeId);


-- count difference between works and works which are missing one upload
select  (select count(1) from Works where HOLLIS is not null) wH , (select count(1) from  Works w
  inner join Volumes v using(workId)
  where  -- WorkName like '%art%'and
        not exists  (select volumeId from DRS d where v.workId = w.workId and d.volumeId = v.volumeId)) wMissingSome;

-- this gets you the works where something not uploaded
select  w.WorkName, w.HOLLIS, v.label, d.DRSdir from DRS d
  inner join Volumes v using(volumeId)
  inner join Works w using (workId)
  where  -- WorkName like '%art%' and
        w.HOLLIS is not null and d.DRSid is not null  ;  -- and
         --  exists  (select volumeId from DRS d where d.volumeId = v.volumeId and v.workId = w.workId) ;
select distinct w.WorkName, w.HOLLIS from  Works w
  inner join Volumes v using(workId)
  where  -- WorkName like '%art%' and
        w.HOLLIS is not null and
          not exists  (select volumeId from DRS d where d.volumeId = v.volumeId and v.workId = w.workId) ;


-- gets the number of volumes per work

-- Hmm, I wonder if 0 in the vd column means the entire work is uploaded
-- This statement definitively shows works with uploads missing
-- GET WORKS WITH MISSING UPLOADS
select workName, HOLLIS
, (select count(1) from Volumes v where v.workId = w.WorkId) vpw,
 (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is not null and v.workId = w.workId) vd
from Works w
  -- get rid of works with outlines and print mastersCALL `drs`.`AddDRS`(<{IngestDate datetime}>, <{objectid varchar(45)}>, <{objectUrn varchar(45)}>, <{DRSdir varchar(45)}>, <{filesCount int(11)}>, <{size bigint(20)}>, <{OSN varchar(45)}>);

    left outer join drs.Outlines o using (workId) left outer join drs.PrintMasters p using (workId)
    inner join Volumes v using (workId)

    where w.HOLLIS is not null
          and p.PrintMasterId is  null
          and o.outLineId is  null
    and
    (select count(1) from Volumes v where v.workId = w.WorkId)
          -- = here means everything uploaded if its not 0
		<>
     (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is not null and v.workId = w.workId)
 --  and WorkName like '%art%'
and
-- where
          (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is null and v.workId = w.workId) <> 0
group by workName;


-- un uploaded volumes: 24558

-- How many works in the catalog
select count(distinct WorkName)  from Works ;

-- How many of those have HOLLIS?
select count(distinct WorkName)  from Works   where HOLLIS is not null ;

-- How many works in the Volumes collection?
select works, worksNoHollis, worksInVolumes - pdw as `works without printmasters`, worksInVolumes - odw as `works without outlines`,works + worksNoHollis, r.worksInVolumes, worksWithoutVolumes + r.worksWithVolumes from  (select

     (select count(distinct WorkName)
      from Works
      where HOLLIS is not null)   works,
     (select count(distinct WorkName)
      from Works
      where HOLLIS is null)         worksNoHollis,
     (select count(distinct workId)
      from Volumes)                 worksInVolumes,
     (select count(distinct W.workId, W.WorkName, W.HOLLIS)
      from Works W
        left join Volumes V using (workId)
      where V.volumeId is NULL)     worksWithoutVolumes,

     (select count(distinct W.workId, W.WorkName, W.HOLLIS)
      from Works W
        left join Volumes V using (workId)
      where V.volumeId is NOT NULL) worksWithVolumes,
  (select count(distinct workId) from PrintMasters) as pdw,
  (select count(workId) from PrintMasters) as pw,
  (select count(distinct workId) from Outlines) as odw,
  (select count(workId) from Outlines) as ow
) as r
;

-- worksWithVolumes should = worksInVolumes
select 13547 + 13739, 26230 + 198, 12683 + 13547;


-- from Volumes V  inner join Works W on v.workId = W.workId
  left join Outlines O on W.workId = O.workId
  left join PrintMasters P on P.workId = W.workId
  left join DRS D on v.volumeId = D.volumeId

; -- where D.DRSid is null and O.outlineId is null and P.PrintMasterId is null;

select count(distinct W.WorkName, W.HOLLIS) from Works;
/* +++++++++++++++++++++++++++++++++++++++++++++++++++++++++    */
/* 			GET WORKS WITH NO MISSING UPLOADS                   */
select count(distinct workName) -- ,  HOLLIS
  -- , (select count(1) from Volumes v where v.workId = w.WorkId) vpw,
  -- (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is not null and v.workId = w.workId) vd
from Works w
  -- get rid of works with outlines and print masters
    left outer join drs.Outlines o using (workId) left outer join drs.PrintMasters p using (workId)
    inner join Volumes v using (workId)

    where w.HOLLIS is not null
          and p.PrintMasterId is  null
          and o.outLineId is  null
    and
    (select count(1) from Volumes v where v.workId = w.WorkId)
          -- = here means everything uploaded if its not 0
          =
     (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is not null and v.workId = w.workId)
 --  and WorkName like '%art%'
-- whereCALL `drs`.`WeeklyStatus`();

-- and   (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is not null and v.workId = w.workId) <> 0
; -- group by workName;


/*------------------ how many works were created when volumes were updated? -----*/
select v.volumeId, v.create_time, w.create_time, v.label, w.workName from Works w inner join Volumes v using (workId) 
where w.create_time < '2018-05-18'  
order by v.create_time desc;

select * from Works where create_time > '2018-05-16' order by create_time asc;

select * from Works where create_time > '2018-05-16' order by workId asc;
select * from Volumes v inner join Works w using (workId) where w.create_time > '2018-05-16' order by w.workId desc, w.create_time desc ; 

select * from Outlines where create_time > '2018-05-14' order by create_time asc;
delete from Works where workId > 13774 ; -- order by Works.create_time asc;
/* -----------------   get all the duplicate works   ------------------------------- */

select w0.workId, w0.workName, w0.HOLLIS from Works w0 inner join 
(
select workId, workName, HOLLIS 
from Works 
group by workName  
having count(workName) > 1) dw
on w0.WorkName = dw.workName 
order by w0.workId asc,w0.WorkName asc ;
select * from Volumes where workId = 7351; 


/* -----------------   get all the duplicate volumes ------------------------------- */
select * from Works where create_time > '2018-06-05' and HOLLIS is NULL order by workName asc;
select v0.workId, v0.volumeId, v0.label from Volumes v0 inner join 
(
select volumeId, workId, label
from drs.Volumes 
group by label
having count(label) > 1) v1
on v0.label = v1.label
order by v0.volumeId asc,v0.label asc ;

-- Old AllReadyWorks
create view AllReadyWorks as
  select distinct
    `w`.`workId`   AS `workId`,
    `w`.`WorkName` AS `WorkName`,
    `w`.`HOLLIS`   AS `HOLLIS`
  from ((`drs`.`Works` `w` left join `drs`.`Outlines` `o` on ((`w`.`workId` = `o`.`workId`))) left join
    `drs`.`PrintMasters` `p` on ((`w`.`workId` = `p`.`workId`)))
  where ((`w`.`HOLLIS` is not null) and isnull(`p`.`PrintMasterId`) and isnull(`o`.`outlineId`));
-- new AllReadyWorks sends up all PrintMasters and OutlineIds

/*
alter view AllReadyWorks as
  select distinct
    `w`.`workId`   AS `workId`,
    `w`.`WorkName` AS `WorkName`,
    `w`.`HOLLIS`   AS `HOLLIS`,
    `o`.OSN AS OutlineOSN,
    p.OSN as PrintMasterOSN
  from ((`drs`.`Works` `w` left join `drs`.`Outlines` `o` on ((`w`.`workId` = `o`.`workId`))) left join
    `drs`.`PrintMasters` `p` on ((`w`.`workId` = `p`.`workId`)))
  where (`w`.`HOLLIS` is not null);
  */

 select distinct
    v.label as 'Volume',
    `w`.`WorkName` AS `WorkName`,
    `w`.`HOLLIS`   AS `HOLLIS`,
    `o`.OSN AS OutlineOSN,
    p.OSN as PrintMasterOSN
  from ((`drs`.`Works` `w` left join `drs`.`Outlines` `o` on ((`w`.`workId` = `o`.`workId`))) left join
    `drs`.`PrintMasters` `p` on ((`w`.`workId` = `p`.`workId`)))
  left join PrintMasters prn on ( prn.workId = w.workId)
 left join Outlines outs on (outs.workId = w.workId)
    left join Volumes v on (v.workId = w.workId)
where
(p.PrintMasterId is null and o.outlineId is null and v.volumeId is not null)
and  (`w`.`HOLLIS` is not null)
order by WorkName asc ;


select (select count( distinct workName ) from AllReadyWorks) arw, (select count(distinct workName) from ReadyWorksNeedsBuilding)  rwnb;


select count(distinct WorkName)  from AllReadyWorks;


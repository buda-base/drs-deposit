use DRSQA; 

select count(distinct workId) from Volumes v

where v.volumeId not in (select volumeId from Outlines  union select volumeId from PrintMasters);
; 
select * from Volumes v where 

v.volumeId not in (select volumeId from Outlines  union select volumeId from PrintMasters);

select workId from Volumes v where volumeId in (select volumeId from Outlines  union select volumeId from PrintMasters) pm;

--  34431 = 32513 + 1918
select 
(select count(workId) from Volumes) w,
(select  count(workId) from Volumes left join (select volumeId from Outlines  union select volumeId from PrintMasters) opm using(volumeId)
where opm.volumeId is  null) noopm,
(select  count(workId) from Volumes left join (select volumeId from Outlines  union select volumeId from PrintMasters) opm using(volumeId)
where opm.volumeId is not null) hasopm;


SELECT DISTINCTrow
        `v`.`volumeId` AS `volumeId`,
        `v`.`label` AS `Volume`,
        `w`.`workId` AS `workId`,
        `w`.`WorkName` AS `WorkName`,
        `w`.`HOLLIS` AS `HOLLIS`,
        NULL AS `OutlineURN`,
        NULL AS `PrintMasterURN`
    FROM
	`DRSQA`.`Works` `w`
    join Volumes v using(workId)
    left join (select volumeId from Outlines  union select volumeId from PrintMasters) opm using(volumeId)
where opm.volumeId is  null
-- AND (`v`.`volumeId` IS NOT NULL)
AND (`w`.`HOLLIS` IS NOT NULL);

    ;
    
    
    
    
SELECT DISTINCTrow
        `v`.`volumeId` AS `volumeId`,
        `v`.`label` AS `Volume`,
        `w`.`workId` AS `workId`,
        `w`.`WorkName` AS `WorkName`,
        `w`.`HOLLIS` AS `HOLLIS`,
        (select objectUrn from DRS d1 
    join Outlines o1 using(volumeId)
    join Volumes vo using(volumeId)
    where vo.workId = w.workId) AS `OutlineUrn`,
        NULL AS `PrintMasterURN`
    FROM
	`DRSQA`.`Works` `w`
    join Volumes v using(workId)
     
    /*-- Remove this line to include outlines and print masters
    -- No we need this to filter out opms from the results
         left join 
		(select volumeId from Outlines  
        union select volumeId from PrintMasters) opm 
        using(volumeId)
	where opm.volumeId is  null
    */
    -- and replace it with the outline and print master DRS entries
    /* TODO DONE: to inlcude outlines and printmasters for a work
    change the left join to 
    (select objectUrn from DRS d1 
    join Outlines o1 using(volumeId)
    join Volumes vo using(volumeId)
    where vo.workId = w.workId) o,  -- so can use o.objectUrn
     (select objectUrn from DRS d2 
    join PrintMasters pm1 using(volumeId)
    join Volumes vo2 using(volumeId)
    where vo2.workId = w.workId) pm,  -- so can use o.objectUrn
    */
   --  and v.volumeId in (32536,34584)
	where (`w`.`HOLLIS` IS NOT NULL)
    order by w.WorkName
    ;

CREATE DEFINER=`bdrc`@`%` PROCEDURE `GetReadyVolumes`(IN fetchBatch int)
    COMMENT 'Return the Ready volumes.  Can return up to fetchBatch result se'
BEGIN


    declare done boolean default 0;
    declare thisWork integer(11);
    
    declare nUnqueuedWorks integer(11);


                                                    
    declare worksC cursor for
        select  workId from tWork;

    declare continue handler for SQLSTATE '02000' set done=1;


-- find 'n' works which have at least 1 not queued
    Create temporary table if not exists tWork as ( select distinct r.workId from Works r
                                                                                      inner join Volumes v on r.workId = v.workId
                                                    where not v.Queued
                                                    order by r.workId asc
                                                    limit fetchBatch);
                                                    
                                                    -- diag select workId as TWORK_WORKID from tWork ;

-- Get the unqueued  volumes for those works
    Create temporary table if not exists tVol as ( select distinct v.volumeId from Works r
                                                                                       inner join Volumes v on r.workId = v.workId
                                                   where not v.Queued and
                                                       v.workId in (select t.workId from tWork t));

-- diag select volumeId as TVOL_VOLID from tVol;
set nUnqueuedWorks = (  select count(distinct r.workId) from Works r
                                                                                      inner join Volumes v on r.workId = v.workId
                                                    where not v.Queued );
                                                    
-- diag select nUnqueuedWorks ;

/*
* -- find 'n' works which have at least 1 not queued
*    Create temporary table if not exists tWork0 as ( select distinct r.workId from ReadyWorksNotDeposited r
*                                                                                       inner join Volumes v on r.Volume = v.label
*                                                     where not v.Queued
*                                                     order by r.workId asc
*                                                     limit fetchBatch);
*
* -- Get the volumes for those works
*    Create temporary table if not exists tVol0 as ( select distinct v.volumeId from ReadyWorksNotDeposited r
*                                                                                        inner join Volumes v on r.Volume = v.label
*                                                    where not v.Queued
*                                                      and v.workId in (select t.workId from tWork t));
*/
-- for diagnosis only. Breaks the Python who calls this
-- select * from Volumes v join tVol tv on tv.volumeId = v.volumeId  ;
 
    open worksC;

    read_loop: LOOP
        fetch worksC into thisWork;
        if done = 1 then
            leave read_loop;
        end if;
        select r.WorkName, r.HOLLIS, v.label as Volume,  v.Queued as Queued, null as OutlineUrn, null as PrintMasterUrn from Works r
                                                                                                            inner join Volumes v on r.workId = v.workId
                                                                                                            inner join	tVol tv on tv.volumeId = v.volumeId
        -- jimk drs-deposit #76 filter out volumes which are queued
        where 
        not v.Queued and v.workId = thisWork
        order by r.workId asc ;
    END LOOP;

    close worksC;
-- diag select t.volumeId from tVol t ;
-- jimk drs-deposit-87. re we updating everything if 

   update Volumes set Queued =  1 where volumeId in (select t.volumeId from tVol t);



END
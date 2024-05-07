CREATE DEFINER=`bdrc`@`%` PROCEDURE `GetReadyVolumes`(IN fetchBatch int)
    COMMENT 'Return the Ready volumes.  Can return up to fetchBatch result sets'
BEGIN


    declare done boolean default 0;
    declare thisWork integer(11);
    
    declare nUnqueuedWorks_pre integer(11);
    declare nUnqueuedVolumes_pre integer(11);

    declare nUnqueuedFetchedWorks integer(11);
    declare nUnqueuedFetchedVolumes integer(11);

    declare nUnqueuedWorks_post integer(11);
    declare nUnqueuedVolumes_post integer(11);

                                                    
    declare worksC cursor for
        select  workId from tWork;

    declare continue handler for SQLSTATE '02000' set done=1;
    
    	DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
SELECT 'SQLException in loop';
    END;

-- find 'n' works which have at least 1 not queued
    Create temporary table if not exists tWork as ( select distinct r.workId from Works r
			inner join Volumes_only v on r.workId = v.workId
		    where not v.Queued
			order by r.workId asc
			limit fetchBatch
            );
                                                    
-- select workId as TWORK_WORKID from tWork ;

-- Get the unqueued  volumes for those works
    Create temporary table if not exists tVol as ( select  distinct v.volumeId  from Works r
                                                                                       inner join Volumes_only v on r.workId = v.workId
                                                   where not v.Queued and
                                                       v.workId in (select t.workId from tWork t));

/** select 'diag';
        select * from tWork;
        select * from tVol;
select 'end diag';
*/

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
/*
 * select * from Volumes v join tVol tv on tv.volumeId = v.volumeId  ;
 */
 
    open worksC;
    

    read_loop: LOOP
        fetch worksC into thisWork;
        if done = 1 then
            leave read_loop;
        end if;
        -- jimk drs-deposit-70 - filter out printmasters and outlines
	SELECT 
		r.WorkName,
		r.HOLLIS,
		v.label AS Volume,
		v.Queued AS Queued,
		NULL AS OutlineUrn,
		NULL AS PrintMasterUrn
	FROM
		Works r
			INNER JOIN
		Volumes_only v ON r.workId = v.workId
			INNER JOIN
		tVol tv ON tv.volumeId = v.volumeId
	WHERE
		NOT v.Queued AND v.workId = thisWork
	ORDER BY r.workId ASC;
			
		-- TODO: Try remove the Volumes V inner join, see what we get
        -- TODO: Insert into summaries
        -- diag_1 is the copy of the output


/* This bombs because unqueued_diag_1 was never created
	  start Transaction;

        insert unqueued_diag_1( LABEL, QUEUED)    
			select  v.label as LABEL,  v.Queued as Queued 
			from Works r
					inner join Volumes_only v on r.workId = v.workId
					inner join	tVol tv on tv.volumeId = v.volumeId

			-- jimk drs-deposit #76 filter out volumes which are queued
			where  not v.Queued 
						and v.workId = thisWork
						order by r.workId asc ;
        commit;
  */      
    END LOOP;

    close worksC;
-- diag select t.volumeId from tVol t ;
-- jimk drs-deposit-87. re we updating everything if 

/***********   diag  **************
 * select volumeId as TVOL_VOLID from tVol;
 **********  END diag  **************/

set nUnqueuedFetchedWorks = ( select count(*) from tWork );
set nUnqueuedFetchedVolumes = (select count(*) from tVol );

set nUnqueuedWorks_pre = (
	select count(distinct r.workId) 
	from Works r
	inner join Volumes_only v on r.workId = v.workId
	where not v.Queued
);

set nUnqueuedVolumes_pre = (
	select count(volumeId) 
	from Volumes_only
	where not Queued
);


UPDATE Volumes 
SET 
    Queued = 1,
    Queued_time = CURRENT_TIMESTAMP
WHERE
    volumeId IN (SELECT 
            t.volumeId
        FROM
            tVol t);

-- take 2
--   update Volumes set 
--   Queued =  1,    Queued_time = CURRENT_TIMESTAMP 
--    where volumeId in (select t.volumeId from tVol t);

set nUnqueuedWorks_post = (
	select count(distinct r.workId) 
	from Works r
	inner join Volumes_only v on r.workId = v.workId
	where not v.Queued
);

set nUnqueuedVolumes_post = (
	select count(volumeId) 
	from Volumes_only
	where not Queued

);


start transaction;

INSERT INTO `drs`.`GetReadyLog`
(`vols_unqueued_pre`,
`vols_unqueued_post`,
`works_unqueued_pre`,
`works_unqueued_post`,
`works_fetched`,
`vols_fetched`)
VALUES
(nUnqueuedVolumes_pre,
nUnqueuedVolumes_post,
nUnqueuedWorks_pre,
nUnqueuedWorks_post,
nUnqueuedFetchedWorks,
nUnqueuedFetchedVolumes
);

commit; 
END

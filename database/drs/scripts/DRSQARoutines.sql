create procedure AddOutline (IN workName varchar(45)) comment 'Creates an outline row. Looks up the workName, adds it if not exists '
BEGIN

set @volumeLabel = concat(workName,'-Outline');

-- Do we have an existing volume?
set @oVolumeId = (select volumeId from Volumes where label = @volumeLabel);

if @oVolumeId is null then
	-- AddVolume adds the work if it has to
	Call AddVolume(workName,@volumeLabel);
    set @oVolumeId = (select volumeId from Volumes v where label = @volumeLabel);

END IF;

insert into Outlines(volumeId) values (@oVolumeId)
on duplicate key update volumeId = @oVolumeId ;

END
;

create procedure AddPrintMaster (IN workName varchar(45))
BEGIN

set @volumeLabel = concat(workName,'-PrintMaster');

-- Do we have an existing volume?
set @pmVolumeId = (select volumeId from Volumes where label = @volumeLabel);

if @pmVolumeId is null then
	-- AddVolume adds the work if it has to
	Call AddVolume(workName,@volumeLabel);
    set @pmVolumeId = (select volumeId from Volumes v where label = @volumeLabel);

END IF;

insert into PrintMasters(volumeId) values (@pmVolumeId)
on duplicate key update volumeId = @pmVolumeId ;

END
;


create procedure BuildOutlines () comment 'Migrates old outline format (in OutlinesOrig) to new volume based format'
BEGIN


declare done boolean default 0;
declare thisWork  varchar(45);

declare worksC cursor for
select WorkName from Works w join OutlinesOrig pm on pm.workId = w.workId  ;

declare continue handler for SQLSTATE '02000' set done=1;

open worksC;

read_loop: LOOP
	fetch worksC into thisWork;
    if done = 1 then
		leave read_loop;
	end if;

	Call AddOutline(thisWork);
END LOOP;

close worksC;

END
;

create procedure BuildPrintMasters () comment 'Migrates old outline format (in PrintMastersOrig) to new volume based format'
BEGIN


declare done boolean default 0;
declare thisWork  varchar(45);

declare worksC cursor for
select WorkName from Works w join PrintMastersOrig pm on pm.workId = w.workId ;

declare continue handler for SQLSTATE '02000' set done=1;

open worksC;

read_loop: LOOP
	fetch worksC into thisWork;
    if done = 1 then
		leave read_loop;
	end if;

	Call AddPrintMaster(thisWork);
END LOOP;

close worksC;

END
;

create procedure GetReadyOutlines (IN fetchBatch int) comment 'Return up to numResults outlines which have not yet been batch built'
BEGIN


create temporary table if not exists oWork
  select distinct o.volumeId,w.WorkName,w.HOLLIS, v.label as Volume from Outlines o
	inner join Volumes v using(volumeId)
  join ReadyWorksNotDeposited w  on w.workId = v.workId
    where not v.Queued limit fetchBatch ;

  -- update Volumes  set Queued = 1 where volumeId in (select volumeId from oWork );

  select WorkName, HOLLIS, Volume, NULL as OutlineUrn, NULL as PrintMasterUrn from oWork;

  drop temporary table oWork;

END
;

create procedure GetReadyPrintMasters (IN fetchBatch int) comment 'Follows GetReadyOutlines template. Returns Works data for printmasters which are ready to build'
BEGIN
create temporary table if not exists oWork
  select distinct o.volumeId,w.WorkName,w.HOLLIS, v.label as Volume from PrintMasters o
	inner join Volumes v using(volumeId)
  join ReadyWorksNotDeposited w  on w.workId = v.workId
    where not v.Queued limit fetchBatch ;

  # update Volumes  set Queued = 1 where volumeId in (select volumeId from oWork );

  select WorkName, HOLLIS, Volume, NULL as OutlineUrn, NULL as PrintMasterUrn from oWork;

  drop temporary table oWork;
END
;


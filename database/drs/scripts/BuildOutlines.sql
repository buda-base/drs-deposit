select workId into @glurm from Works where w.WorkName = "HINOT HERER";

if @glurm is not null
BEGIN
selet @glurm;


CREATE DEFINER=`bdrc`@`%` PROCEDURE `AddOutline`(workName varchar(45))
    COMMENT 'Creates an outline row, and corresponding volumeRow Looks up the workName, adds it if not exists '
BEGIN



if not exists (select workId from Works w where w.workName = workName) then
BEGIN
	call AddWork(workName,NULL);
END;
END IF;

-- build the label
select concat('outline',workId) into @outlineVolumelabel;

select workId into @outlineWorkId from Works w where w.workName = workName;

if not exists (select volumeId from Volumes v where V.label = @outlineVolumeLabel) then
BEGIN
	insert into Volumes (workId, label) 
    
END;
END IF;

insert into Outlines(workId,volumeId) values
((select workId from Works w where w.workName = workName)) 

on duplicate key update workId = workId ;

END

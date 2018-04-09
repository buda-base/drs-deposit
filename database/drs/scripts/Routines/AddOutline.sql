CREATE DEFINER=`bdrc`@`%` PROCEDURE `AddOutline`(workName varchar(45), outlineText TEXT)
    COMMENT 'Creates an outline row. Looks up the workName, adds it if not exists '
BEGIN


-- The work might not be in the db yet
if not exists (select workId from Works w where w.workName = workName) then
BEGIN
	insert into Works(workName) values(workName);
	insert into Outlines(workId, workOutline) values (last_insert_id(), outlineText);
END;
else
-- the work exists

insert into Outlines(workId,workOutline) values
((select workId from Works w where w.workName = workName), outlineText) 
-- jsk: temporarily defeat load on duplicate key update workOutline = outlineText;
on duplicate key update workId = workId ;
END IF;
END
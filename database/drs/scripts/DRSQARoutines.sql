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


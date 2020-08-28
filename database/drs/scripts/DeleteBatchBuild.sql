CREATE DEFINER=`bdrc`@`%` PROCEDURE `DeleteBatchBuild`(IN batchBuildPath varchar(255))
    COMMENT 'Deletes a batch build and updates the contained volumes metadata'
BEGIN

    declare v_buildPathId  INTEGER(11);
    declare v_batchBuildId INTEGER(11);

    set v_buildPathId = ( select buildPathId from BuildPaths where BuildPath = batchBuildPath);
    set v_batchBuildId =( select batchBuildId from BatchBuilds where v_buildPathId = BatchBuilds.buildPathId);
    
    -- select label, Queued from Volumes where batchBuildId = v_batchBuildId ; 

    update Volumes v set Queued = 0, batchBuildId = null  where v.batchBuildId = batchBuildId;
    delete from BatchBuilds  where batchBuildId = BatchBuilds.batchBuildId;
	delete from BuildPaths where buildPathId = BuildPaths.buildPathId;
end
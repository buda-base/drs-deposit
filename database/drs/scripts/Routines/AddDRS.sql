CREATE PROCEDURE `AddDRS` (
  IngestDate datetime
  ,  objectid varchar(45) 
  , objectUrn varchar(45)
  , DRSdir varchar(45) 
  , filesCount int(11) 
  , size bigint(20)
  , OSN varchar(45)
  )
  BEGIN
  set  @volId = (select volumeId from Volumes where label = OSN);
  
INSERT INTO `drs`.`DRS`
(
`IngestDate`,
`objectid`,
`DRSdir`,
`objectUrn`,
`filesCount`,
`size`,
`OSN`,
`volumeId`)
VALUES
(
  IngestDate 
  ,  objectid 
  , objectUrn
  , DRSdir
  , filesCount
  , size
  , OSN 
  , @volId
  );
END
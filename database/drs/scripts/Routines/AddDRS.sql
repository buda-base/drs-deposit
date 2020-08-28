CREATE DEFINER=`bdrc`@`%` PROCEDURE `AddDRS`(
  IngestDate datetime
  ,  objectid varchar(45) 
  , objectUrn varchar(72)
  , DRSdir varchar(45) 
  , filesCount int(11) 
  , size bigint(20)
  , OSN varchar(45)
  )
BEGIN
  
INSERT INTO `DRS`
(
`IngestDate`,
`objectid`,
`DRSdir`,
`objectUrn`,
`filesCount`,
`size`,
`OSN`)
VALUES
(
  IngestDate 
  ,  objectid 
  , DRSdir
  , objectUrn  
  , filesCount
  , size
  , OSN 
  )
  on duplicate key update
  `IngestDate` = IngestDate,
`objectid` = objectid,
`DRSdir`= DRSdir,
`objectUrn`= objectUrn,
`filesCount` = filesCount,
`size` = size,
`OSN` = OSN ;

END
# select * from BatchBuilds where buildPathId in (66405, 66406);

#
# INSERT INTO `drs`.`BatchBuilds`
# (
# `BuildDate`,
# `Result`,
# `buildPathId`)
# VALUES
# (CURRENT_TIMESTAMP(),"success",66406);
#
# INSERT INTO `drs`.`Volumes`
# (`workId`,
# `label`,
# `batchBuildId`,
# `builtFileSize`,
# `builtFileCount`,
# `Queued`)
# VALUES
# (1,
# 'TestDeletion83934',
# 83934,
# 4242,
# 42,
# b'1');

# INSERT INTO `drs`.`DRS`
# (
# `IngestDate`,
# `objectid`,
# `DRSdir`,
# `objectUrn`,
# `filesCount`,
# `size`,
# `OSN`)
# VALUES
# (
# CURRENT_TIME(),
# 4225,
# 'Harkabeeparolyn-1n',
# 'urn42:4225',
# 22,
# 4243,
# 'TestDeletion83934');

#
# update Volumes set label = 'TestDeletion83933' where volumeId = 32521;
# select * from Volumes where  create_time > '2018-08-01';
#
# select * from DRS order by create_time desc limit 4;
#
# select * from Volumes join DRS using(volumeId) where volumeId =  32521;
#
# update DRS set OSN = (select label from Volumes where volumeId = 32521) where objectid = 4322;


# Bad objects volume Queued volume = false
# update Volumes set Queued =False

-- select * from
update
Volumes
set Queued = False
where volumeId in (select volumeId from DRS where objectid in (select oid from badObjectsWithDates ));

# find and delete build paths
# modify this query to delete instead of select *
# select BuildPaths.*

delete from BuildPaths where buildPathid in (
select distinct buildPathId from BatchBuilds 
join Volumes using(batchBuildId)
join DRS d using (volumeId) 
join badObjectsWithDates b on d.objectid = b.oid) ;

# validate buildPathId is null in this query after above delete run
# modify this query to delete instead of select *
# select *
delete
from BatchBuilds     where batchBuildId in ( select batchBuildId from  Volumes v  join DRS using (volumeId)
                                                         where objectid in (select oid from badObjectsWithDates)
                                                         );
# and last
# select *
delete
from DRS where objectid in (select oid from badObjectsWithDates);


# drop view objdel2296;
# drop VIEW `objdel2972`
# drop VIEW `objdel4976`
# Create the views to hold the data
# CREATE VIEW `objdel2296` AS select oid from objectIds_2296267052537190368;
# CREATE VIEW `objdel2972` AS select oid from objectIds_2972054413433176357;
# CREATE VIEW `objdel4976` AS select oid from objectIds_4976341152669192669;
# CREATE VIEW `objdel4985` AS select oid from objectIds_4985187898885511212;
# CREATE VIEW `objdel6656` AS select oid from objectIds_6656675068004768366;
# CREATE VIEW `objdel7200` AS select oid from objectIds_7200278857549300325;
# CREATE VIEW `objdel7233` AS select oid from objectIds_7233437762511080852;
#
select count(*) from DRS
call WeeklyStatus()

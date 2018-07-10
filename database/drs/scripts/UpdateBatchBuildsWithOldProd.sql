 create  table new_table (
   label varchar(45) not null,
   path varchar(255) not null
 );

insert into new_table (label, path) select
                                         label,       bbs.batchBuildPath as path
                                       from bbs
                                         inner join DRS on bbs.batchBuildName = DRS.DRSdir
                                         inner join Volumes v on v.volumeId in (select volumeId
                                                                                from DRS drs1
                                                                                where drs1.DRSDir = DRS.DRSdir);

select * from new_table limit 10;
select count(*) from bbs ;
drop table new_table;


UpdateBatchBuildsFromProd
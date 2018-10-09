create view AllReadyWorks as
  select distinct `v`.`volumeId`                          AS `volumeId`,
                  `v`.`label`                             AS `Volume`,
                  `w`.`workId`                            AS `workId`,
                  `w`.`WorkName`                          AS `WorkName`,
                  `w`.`HOLLIS`                            AS `HOLLIS`,
                  (select `d1`.`objectUrn`
                   from ((`DRSQA`.`DRS` `d1` join `DRSQA`.`Outlines` `o1` on ((`d1`.`volumeId` =
                                                                               `o1`.`volumeId`))) join `DRSQA`.`Volumes` `vo` on ((
                     `d1`.`volumeId` = `vo`.`volumeId`)))
                   where (`vo`.`workId` = `w`.`workId`))  AS `OutlineUrn`,
                  (select `d2`.`objectUrn`
                   from ((`DRSQA`.`DRS` `d2` join `DRSQA`.`PrintMasters` `pm1` on ((`d2`.`volumeId` =
                                                                                    `pm1`.`volumeId`))) join `DRSQA`.`Volumes` `vo2` on ((
                     `d2`.`volumeId` = `vo2`.`volumeId`)))
                   where (`vo2`.`workId` = `w`.`workId`)) AS `PrintMasterUrn`
  from (`DRSQA`.`Works` `w` join `DRSQA`.`Volumes` `v` on ((`w`.`workId` = `v`.`workId`)))
  where ((`w`.`HOLLIS` is not null) and
         (not(`v`.`volumeId` in (select `DRSQA`.`Outlines`.`volumeId` from `DRSQA`.`Outlines`))) and
         (not(`v`.`volumeId` in (select `DRSQA`.`PrintMasters`.`volumeId` from `DRSQA`.`PrintMasters`))))
  order by `w`.`WorkName`;

create view AllReadyWorksOPM as
  select distinct `v`.`volumeId`                          AS `volumeId`,
                  `v`.`label`                             AS `Volume`,
                  `w`.`workId`                            AS `workId`,
                  `w`.`WorkName`                          AS `WorkName`,
                  `w`.`HOLLIS`                            AS `HOLLIS`,
                  (select `d1`.`objectUrn`
                   from ((`DRSQA`.`DRS` `d1` join `DRSQA`.`Outlines` `o1` on ((`d1`.`volumeId` =
                                                                               `o1`.`volumeId`))) join `DRSQA`.`Volumes` `vo` on ((
                     `d1`.`volumeId` = `vo`.`volumeId`)))
                   where (`vo`.`workId` = `w`.`workId`))  AS `OutlineUrn`,
                  (select `d2`.`objectUrn`
                   from ((`DRSQA`.`DRS` `d2` join `DRSQA`.`PrintMasters` `pm1` on ((`d2`.`volumeId` =
                                                                                    `pm1`.`volumeId`))) join `DRSQA`.`Volumes` `vo2` on ((
                     `d2`.`volumeId` = `vo2`.`volumeId`)))
                   where (`vo2`.`workId` = `w`.`workId`)) AS `PrintMasterUrn`
  from (`DRSQA`.`Works` `w` join `DRSQA`.`Volumes` `v` on ((`w`.`workId` = `v`.`workId`)))
  where ((`w`.`HOLLIS` is not null) and
         (not(`v`.`volumeId` in (select `DRSQA`.`Outlines`.`volumeId` from `DRSQA`.`Outlines`))) and
         (not(`v`.`volumeId` in (select `DRSQA`.`PrintMasters`.`volumeId` from `DRSQA`.`PrintMasters`))))
  order by `w`.`WorkName`;


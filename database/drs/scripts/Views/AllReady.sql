CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `bdrc`@`%` 
    SQL SECURITY DEFINER
VIEW `AllReadyWorks` AS
    SELECT 
        `w`.`workId` AS `workId`,
        `w`.`WorkName` AS `WorkName`,
        `w`.`HOLLIS` AS `HOLLIS`,
        `w`.`create_time` AS `create_time`,
        `w`.`update_time` AS `update_time`
    FROM
        ((`Works` `w`
        LEFT JOIN `Outlines` `o` ON ((`w`.`workId` = `o`.`workId`)))
        LEFT JOIN `PrintMasters` `p` ON ((`w`.`workId` = `p`.`workId`)))
    WHERE
        (ISNULL(`p`.`PrintMasterId`)
            AND ISNULL(`o`.`outlineId`))
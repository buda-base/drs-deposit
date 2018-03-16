-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema drs
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema drs
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `drs` DEFAULT CHARACTER SET latin1 ;
USE `drs` ;
USE `drs` ;

-- -----------------------------------------------------
-- procedure AddOutline
-- -----------------------------------------------------

USE `drs`;
DROP procedure IF EXISTS `drs`.`AddOutline`;

DELIMITER $$
USE `drs`$$
CREATE PROCEDURE `AddOutline` (workName varchar(45), outlineText varchar(255))
COMMENT 'Creates an outline row. Looks up the workName, adds it if not exists '
BEGIN


if not exists (select workId from DRS.Works w where w.workName = workName) then
BEGIN
	insert into DRS.Works(workName) values(workName);
	insert into DRS.Outlines(workId, workOutline) values (last_inserted(), outlineText);
END;
else
insert into DRS.outlines(workId,workOutline) values
((select workId from DRS.Works w where w.workName = workName), outlineText);
END IF;
END$$

DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

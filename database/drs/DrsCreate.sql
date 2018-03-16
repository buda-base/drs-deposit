-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema drs
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema drs
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `drs` DEFAULT CHARACTER SET latin1 ;
USE `drs` ;

-- -----------------------------------------------------
-- Table `drs`.`BatchStatus`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `drs`.`BatchStatus` ;

CREATE TABLE IF NOT EXISTS `drs`.`BatchStatus` (
  `idBatchStatus` INT(11) NOT NULL,
  `BuildDate` DATETIME NULL DEFAULT NULL,
  `BuildPath` VARCHAR(255) NULL DEFAULT NULL,
  `BuildRC` VARCHAR(45) NULL DEFAULT '-1' COMMENT 'System result on build (0 is success)',
  `UploadDate` DATETIME NULL DEFAULT NULL,
  `UploadRC` VARCHAR(45) NULL DEFAULT NULL COMMENT 'System result of upload 0 is success -1 is default. Other values are undefined.',
  `HULObject` VARCHAR(45) NULL DEFAULT NULL COMMENT 'HUL Generated OBJ-ID',
  `create_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`idBatchStatus`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `drs`.`Works`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `drs`.`Works` ;

CREATE TABLE IF NOT EXISTS `drs`.`Works` (
  `workId` INT(11) NOT NULL AUTO_INCREMENT,
  `WorkName` VARCHAR(45) NULL DEFAULT NULL,
  `HOLLIS` VARCHAR(45) NULL,
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`workId`),
  UNIQUE INDEX `workId_UNIQUE` (`workId` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `drs`.`Outlines`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `drs`.`Outlines` ;

CREATE TABLE IF NOT EXISTS `drs`.`Outlines` (
  `idOutlines` INT(11) NOT NULL,
  `WorkId` INT(11) NOT NULL,
  `create_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`idOutlines`),
  INDEX `OutlineToWork_idx` (`WorkId` ASC),
  CONSTRAINT `OutlineToWork`
    FOREIGN KEY (`WorkId`)
    REFERENCES `drs`.`Works` (`workId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `drs`.`Volume`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `drs`.`Volume` ;

CREATE TABLE IF NOT EXISTS `drs`.`Volume` (
  `idVolume` INT(11) NOT NULL AUTO_INCREMENT,
  `workId` INT(11) NULL DEFAULT NULL,
  `batchId` INT(11) NULL DEFAULT NULL,
  `create_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`idVolume`),
  INDEX `VolToWork_idx` (`workId` ASC),
  INDEX `VolToBatch_idx` (`batchId` ASC),
  CONSTRAINT `VolToBatch`
    FOREIGN KEY (`batchId`)
    REFERENCES `drs`.`BatchStatus` (`idBatchStatus`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `VolToWork`
    FOREIGN KEY (`workId`)
    REFERENCES `drs`.`Works` (`workId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

ALTER TABLE PrintMasters modify COLUMN update_time SET DEFAULT current_time on update current_time;
ALTER TABLE PrintMasters ADD volumeId int(11 NOT NULL;
CREATE UNIQUE INDEX PrintMasters_volumeId_uindex ON PrintMasters (volumeId);
CREATE INDEX PrintMasters_create_time_index ON PrintMasters (create_time);
ALTER TABLE PrintMasters
ADD CONSTRAINT PrintMaster_Volume_FK
FOREIGN KEY (volumeId) REFERENCES Volumes (volumeId) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE PrintMasters DROP workId;
DROP INDEX idBatchStatus_idx ON PrintMasters;
ALTER TABLE PrintMasters DROP idBatchStatus;
DROP INDEX OSN_UNIQUE ON PrintMasters;
DROP INDEX OSN_UNIQUE ON PrintMasters;
ALTER TABLE PrintMasters DROP OSN;
DROP INDEX PrintMasters_FileURN_uindex ON PrintMasters;
DROP INDEX PrintMasters_FileURN_uindex ON PrintMasters;
ALTER TABLE PrintMasters DROP FileURN;


ALTER TABLE Outlines ADD volumeId int(11) NOT NULL;
CREATE UNIQUE INDEX Outlines_volumeId_uindex ON Outlines (volumeId);
ALTER TABLE Outlines
ADD CONSTRAINT Outlines_Volume__fk
FOREIGN KEY (volumeId) REFERENCES Volumes (volumeId) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE Outlines ALTER COLUMN update_time SET DEFAULT current_time on update current_time;
ALTER TABLE Outlines DROP FOREIGN KEY OutlineToWork;
DROP INDEX OutlineToWork_idx ON Outlines;
ALTER TABLE Outlines DROP workId;
ALTER TABLE Outlines DROP outlineText;
ALTER TABLE Outlines DROP idBatchStatus;
DROP INDEX OSN_UNIQUE ON Outlines;
DROP INDEX OSN_UNIQUE ON Outlines;
ALTER TABLE Outlines DROP OSN;
DROP INDEX Outlines_FileURN_uindex ON Outlines;
ALTER TABLE Outlines DROP FileURN;
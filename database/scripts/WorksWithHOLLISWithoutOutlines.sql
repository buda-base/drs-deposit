SELECT workName, HOLLIS  FROM drs.Works left outer join drs.Outlines using (idWork) where Outlines.idWork is null and Works.HOLLIS is not null; 

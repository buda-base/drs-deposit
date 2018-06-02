-- Hmm, I wonder if 0 in the vd column means the entire work is uploaded
select workName, HOLLIS, (select count(1) from Volumes v where v.workId = w.WorkId) vpw,
  (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is null and v.workId = w.workId) vd
from Works w join Volumes v using (workId)
where   (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is null and v.workId = w.workId) <> 0
group by workName;

select * from Works join Volumes using (workId) left join DRS using(volumeId) where WorkName like '%W1KG4313%';

select count(1 ) from drs.PrintMasters;


-- I think this is it. This is the query for partially uploaded works
select workName, HOLLIS, vpw, vd from (
select workName, HOLLIS, (select count(1) from Volumes v where v.workId = w.WorkId ) vpw,
  (select count(1) from Volumes v left join DRS d using (volumeId) where d.DRSid is not null and v.workId = w.workId) vd
from Works w join Volumes v using (workId)
group by workName) as res

  -- lets have some fun
  -- this tells us which are partially uploaded.
where ( vd = 0
        or (vd <> 0 and  vd <> vpw))
      and HOLLIS is not null
order by vd desc;
;








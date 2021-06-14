create table if not EXISTS flights (
  bid bigint,
  fid bigint,
  price DOUBLE PRECISION,
  PRIMARY KEY (bid)
);

insert into flights(bid, fid, price) values(1, 1, 1.0);
insert into flights(bid, fid, price) values(2, 2, 2.0);
insert into flights(bid, fid, price) values(3, 3, 3.0);
insert into flights(bid, fid, price) values(4, 4, 4.0);
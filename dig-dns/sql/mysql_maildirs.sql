--drop table maildirs;
create table maildirs (id bigint not null auto_increment, path varchar(256) not null, primary key (id));

insert into maildirs (path) values ('roger/');
insert into maildirs (path) values ('anna/');
insert into maildirs (path) values ('mamka/');
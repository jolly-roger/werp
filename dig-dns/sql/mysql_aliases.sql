drop table aliases;
create table aliases (id bigint not null auto_increment, alias varchar(256) not null, is_group boolean not null default false, primary key (id));

insert into aliases (alias, is_group) values ('postmaster', false);
insert into aliases (alias, is_group) values ('igor.onyshchenko', false);
insert into aliases (alias, is_group) values ('hr', false);
insert into aliases (alias, is_group) values ('info', true);
insert into aliases (alias, is_group) values ('sale', true);
insert into aliases (alias, is_group) values ('mail', true);
insert into aliases (alias, is_group) values ('root', true);
insert into aliases (alias, is_group) values ('contact', true);
insert into aliases (alias, is_group) values ('sales', true);
insert into aliases (alias, is_group) values ('office', true);
insert into aliases (alias, is_group) values ('ceo', true);
insert into aliases (alias, is_group) values ('reception', true);
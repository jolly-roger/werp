--drop table domains;
create table domains (id bigint not null auto_increment, domain varchar(256) not null, primary key (id));

insert into domains (domain) values ('dig-dns.com');
insert into domains (domain) values ('uatrains.com');
insert into domains (domain) values ('ukrainianside.com');
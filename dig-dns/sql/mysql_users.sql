drop table users;
create table users (id bigint not null auto_increment, name varchar(256) not null, password varchar(256) not null, primary key (id));

insert into users (name, password) values ('roger', '23ee0084cb55f5f0c6e5ff3b8f0efa4cc1c2dea9f4e5e2551543dacdb67375f1');
insert into users (name, password) values ('anna', '23ee0084cb55f5f0c6e5ff3b8f0efa4cc1c2dea9f4e5e2551543dacdb67375f1');
insert into users (name, password) values ('mamka', '1406cdbe7145db5437ee4da9aa43d653db807cac7e4a3acf2f8708a16853dfa8');
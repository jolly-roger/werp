--drop table alias_user;
create table alias_user (user_id bigint not null, alias_id bigint not null);

-- alias_id | user_id 
------------+---------
--        1 |       3
--        2 |       3
--        3 |       3
--        4 |       3
--        5 |       3
--        3 |       6
--        4 |       6
--        5 |       6
--        6 |       6
--        7 |       3
--        8 |       3
--        7 |       6
--        8 |       6
--        6 |       3
--        9 |       3
--        9 |       6
--       10 |       6
--       10 |       3
--       11 |       3
--       11 |       6
--       12 |       6
--       12 |       3

insert into alias_user (user_id, alias_id) values (1, 1);
insert into alias_user (user_id, alias_id) values (1, 2);
insert into alias_user (user_id, alias_id) values (1, 3);
insert into alias_user (user_id, alias_id) values (1, 4);
insert into alias_user (user_id, alias_id) values (1, 5);
insert into alias_user (user_id, alias_id) values (2, 3);
insert into alias_user (user_id, alias_id) values (2, 4);
insert into alias_user (user_id, alias_id) values (2, 5);
insert into alias_user (user_id, alias_id) values (2, 6);
insert into alias_user (user_id, alias_id) values (1, 7);
insert into alias_user (user_id, alias_id) values (1, 8);
insert into alias_user (user_id, alias_id) values (2, 7);
insert into alias_user (user_id, alias_id) values (2, 8);
insert into alias_user (user_id, alias_id) values (1, 6);
insert into alias_user (user_id, alias_id) values (1, 9);
insert into alias_user (user_id, alias_id) values (2, 9);
insert into alias_user (user_id, alias_id) values (2, 10);
insert into alias_user (user_id, alias_id) values (1, 10);
insert into alias_user (user_id, alias_id) values (1, 11);
insert into alias_user (user_id, alias_id) values (2, 11);
insert into alias_user (user_id, alias_id) values (2, 12);
insert into alias_user (user_id, alias_id) values (1, 12);
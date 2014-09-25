drop table mailboxes;
create table mailboxes (id bigint not null auto_increment, user_id bigint not null, domain_id bigint not null, maildir_id bigint not null, primary key (id));

-- maildir_id | domain_id | user_id | id 
--------------+-----------+---------+----
--          3 |         0 |       3 | 14
--          3 |         7 |       3 | 21
--          3 |        10 |       3 | 24
--          4 |         0 |       6 | 47
--          4 |         7 |       6 | 54
--          4 |        10 |       6 | 57
--          5 |         0 |       7 | 58
--          5 |         7 |       7 | 65
--          5 |        10 |       7 | 68

insert into mailboxes (user_id, domain_id, maildir_id) values (1, 1, 1);
insert into mailboxes (user_id, domain_id, maildir_id) values (1, 2, 1);
insert into mailboxes (user_id, domain_id, maildir_id) values (1, 3, 1);
insert into mailboxes (user_id, domain_id, maildir_id) values (2, 1, 2);
insert into mailboxes (user_id, domain_id, maildir_id) values (2, 2, 2);
insert into mailboxes (user_id, domain_id, maildir_id) values (2, 3, 2);
insert into mailboxes (user_id, domain_id, maildir_id) values (3, 1, 3);
insert into mailboxes (user_id, domain_id, maildir_id) values (3, 2, 3);
insert into mailboxes (user_id, domain_id, maildir_id) values (3, 3, 3);

--drop view dovecot_mailboxes;
create view dovecot_mailboxes as
select concat(u.name, '@', d.domain) as email,
    u.name as user,
    u.password,
    concat(main_d.domain, '/', md.path) as path,
    concat('/home/mailer/', main_d.domain, '/', md.path) AS home,
    concat('maildir:/home/mailer/', main_d.domain, '/', md.path) AS maildir,
    5003 AS uid,
    5003 AS gid
from mailboxes as mb
inner join users as u on mb.user_id = u.id
inner join domains as d on mb.domain_id = d.id
inner join domains as main_d on mb.main_domain_id = main_d.id
inner join maildirs md ON mb.maildir_id = md.id;
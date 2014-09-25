create view dovecot_users as
select (u.name || '@' || d.domain) as user,
    ('/home/mailer/' || md.path) AS home,
    ('maildir:/home/mailer/' || md.path) AS mail,
    5003 AS uid,
    5003 AS gid
from mailboxes as mb
inner join users as u on mb.user_id = u.id
inner join domains as d on mb.domain_id = d.id
inner join maildirs md ON mb.maildir_id = md.id;

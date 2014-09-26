create view postfix_mailboxes as
select md.path as path,
    concat(u.name, '@', d.domain) as email, 
    u.name as user
from mailboxes as mb
inner join maildirs as md on mb.maildir_id = md.id
inner join users as u on mb.user_id = u.id
inner join domains as d on mb.domain_id = d.id
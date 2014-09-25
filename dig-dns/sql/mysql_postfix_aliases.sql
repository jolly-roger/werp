create view postfix_aliases as
SELECT concat(a.alias, '@', d.domain) AS alias,
    concat(u.name, '@', d.domain) AS address
   FROM mailboxes m
     JOIN alias_user au ON m.user_id = au.user_id
     JOIN aliases a ON au.alias_id = a.id
     JOIN domains d ON m.domain_id = d.id
     JOIN users u ON m.user_id = u.id
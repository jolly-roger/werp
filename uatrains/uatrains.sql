create sequence id_route_seq minvalue 0 start 0;


create table route (
	id bigint primary key not null default nextval('id_route_seq'),
    rid bigint,
	name varchar(255)
);

create sequence id_spider_seq minvalue 0 start 0;


create table spider (
	id bigint primary key not null default nextval('id_spider_seq'),
    date timestamp
);

create sequence id_station_seq minvalue 0 start 0;


create table station (
	id bigint primary key not null default nextval('id_station_seq'),
    title varchar(255),
    value varchar(255)
);


CREATE OR REPLACE FUNCTION train_station_h_fn() RETURNS trigger AS $$
declare
    local_htype integer;
    local_ts train_station%rowtype;
BEGIN
    if lower(tg_op) = 'insert' then
        local_htype = 0;
        local_ts = new;
    elsif lower(tg_op) = 'update' then
        local_htype = 1;
        local_ts = old;
    elsif lower(tg_op) = 'delete' then
        local_htype = 2;
        local_ts = old;
    end if;
    
    insert into htrain_station(train_station_id, t_id, s_id, arrival, departure, halt, date_from,
        date_to, "order", c_date, htype) values (local_ts.id, local_ts.t_id, local_ts.s_id, local_ts.arrival,
        local_ts.departure, local_ts.halt, local_ts.date_from, local_ts.date_to, local_ts."order", local_ts.c_date,
        local_htype);
    return null;
END;
$$  LANGUAGE plpgsql;


create trigger train_station_h_trg after insert or update or delete
    on train_station for each row execute procedure train_station_h_fn();
    
    
CREATE OR REPLACE FUNCTION train_h_fn() RETURNS trigger AS $$
declare
    local_htype integer;
    local_t train%rowtype;
BEGIN
    if lower(tg_op) = 'insert' then
        local_htype = 0;
        local_t = new;
    elsif lower(tg_op) = 'update' then
        local_htype = 1;
        local_t = old;
    elsif lower(tg_op) = 'delete' then
        local_htype = 2;
        local_t = old;
    end if;
    
    insert into htrain(train_id, value, tid, c_date, htype) values (local_t.id, local_t.value, local_t.tid,
        local_t.c_date, local_htype);
    return null;
END;
$$  LANGUAGE plpgsql;


create trigger train_h_trg after insert or update or delete
    on train for each row execute procedure train_h_fn();
    

CREATE OR REPLACE FUNCTION station_h_fn() RETURNS trigger AS $$
declare
    local_htype integer;
    local_s station%rowtype;
BEGIN
    if lower(tg_op) = 'insert' then
        local_htype = 0;
        local_s = new;
    elsif lower(tg_op) = 'update' then
        local_htype = 1;
        local_s = old;
    elsif lower(tg_op) = 'delete' then
        local_htype = 2;
        local_s = old;
    end if;
    
    insert into hstation(station_id, sid, c_date, htype) values (local_s.id, local_s.sid, local_s.c_date, local_htype);
    return null;
END;
$$  LANGUAGE plpgsql;


create trigger station_h_trg after insert or update or delete
    on station for each row execute procedure station_h_fn();
    
    
CREATE OR REPLACE FUNCTION e_h_fn() RETURNS trigger AS $$
declare
    local_htype integer;
    local_e e%rowtype;
BEGIN
    if lower(tg_op) = 'insert' then
        local_htype = 0;
        local_e = new;
    elsif lower(tg_op) = 'update' then
        local_htype = 1;
        local_e = old;
        if old.vc != new.vc then
            return null;
        end if;
    elsif lower(tg_op) = 'delete' then
        local_htype = 2;
        local_e = old;
    end if;
    
    insert into he(eid, etype, value, oid, ua_title, ru_title, en_title, vc, ua_period, ru_period, en_period,
        c_date, htype) values (local_e.id, local_e.etype, local_e.value, local_e.oid, local_e.ua_title, local_e.ru_title,
        local_e.en_title, local_e.vc, local_e.ua_period, local_e.ru_period, local_e.en_period, local_e.c_date,
        local_htype);
    return null;
END;
$$  LANGUAGE plpgsql;


create trigger e_h_trg after insert or update or delete
    on e for each row execute procedure e_h_fn();
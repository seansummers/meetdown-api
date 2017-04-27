drop table if exists groups;
create table groups (
  id integer primary key autoincrement,
  name text not null
);

drop table if exists events;
create table events (
  id integer primary key autoincrement,
  title text not null,
  location text not null,
  group_id integer not null,
  FOREIGN KEY(group_id) REFERENCES groups(id)
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null,
  email text not null,
  bestfriend_id integer,
  FOREIGN KEY(bestfriend_id) REFERENCES users(id)
);

drop table if exists memberships;
create table memberships (
  id integer primary key autoincrement,
  user_id integer not null,
  group_id integer not null,
  FOREIGN KEY(group_id) REFERENCES groups(id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

drop table if exists signups;
create table signups (
  id integer primary key autoincrement,
  event_id integer not null,
  user_id integer not null,
  FOREIGN KEY(event_id) REFERENCES events(id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

insert into users values(0, 'Pikachu', 'pika@chu.com', 1);
insert into users values(1, 'Evee', 'e@vee.com', 0);
insert into groups values(0, 'Ketchup Lovers');
insert into groups values(1, 'Pyladies');
insert into events (id, title, location, group_id) values(0, 'Ketchup Party!', 'A field', 0);
insert into events (id, title, location, group_id) values(1, 'Chocolate', 'Sugarland', 0);
insert into memberships (id, user_id, group_id) values (0, 0, 0);
insert into signups (id, event_id, user_id) values (0, 0, 0);
insert into signups (id, event_id, user_id) values (1, 1, 0);

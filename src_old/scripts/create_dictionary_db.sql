-- A script for setting up an empty dictionary DB.
-- Contains a template that should be followed by all dictionary tables.

drop table if exists template;

create table template (
       id integer primary key not null,
       `string_id` text not null,
       entry text not null,
       `short_meaning` text,
       meaning text,
       examples text,
       comments text
);

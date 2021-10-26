-- global/state.sql

select current_user(), current_role(), current_warehouse(), current_database(), current_schema(), current_session(), current_ip_address();

show locks;

show transactions;

show tasks;

show databases;

@try:
show objects in {{settings.database}}.{{settings.schema}};

#-- show schemas in database {{settings.database}};

#-- show terse tables;

#-- show views;

#-- show user functions;

show variables;

show parameters;

list @~/;



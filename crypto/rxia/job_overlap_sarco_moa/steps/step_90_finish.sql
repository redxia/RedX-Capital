--------------------------------------------------------------------
-- SYSTEM INFO
--------------------------------------------------------------------

select current_user(), current_role(), current_warehouse(), current_database(), current_schema(), current_session();

show locks;

show transactions;

show databases;

show schemas in database {{DATABASE}};

#-- show terse tables;

#-- show views;

#-- show user functions;

show variables;

show parameters;

--------------------------------------------------------------------
-- DONE
--------------------------------------------------------------------



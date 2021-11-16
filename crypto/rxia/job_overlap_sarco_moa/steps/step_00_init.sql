-----------------------------------------------------------------
-- SESSION SETTINGS
-----------------------------------------------------------------

:: set DATABASE = settings.database 
:: set SCHEMA = settings.schema

:: set DBS = DATABASE + '.' + SCHEMA

use {{DBS}};

--alter session set timezone = 'America/New_York';
alter session set timezone = 'UTC';

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

-----------------------------------------------------------------
-- SESSION SETTINGS
-----------------------------------------------------------------

:: set IDBS = settings.database + '.' + settings.build_schema + settings.cut_date

use {{IDBS}};

--alter session set timezone = 'America/New_York';
alter session set timezone = 'UTC';

--------------------------------------------------------------------
-- SYSTEM INFO
--------------------------------------------------------------------

select current_user(), current_role(), current_warehouse(), current_database(), current_schema(), current_session();

show locks;

show transactions;

show databases;

#-- show terse tables;

#-- show views;

#-- show user functions;

show variables;

show parameters;

--------------------------------------------------------------------
-- DONE
--------------------------------------------------------------------

-----------------------------------------------------------------
-- INIT
-----------------------------------------------------------------

use role {{settings.role}};

use warehouse {{settings.warehouse}};

:: set DATABASE = settings.database
:: set SCHEMA = settings.schema
:: set DBS = DATABASE + '.' + SCHEMA

:: if DATABASE.upper in ['TEMP']
    create schema if not exists {{DBS}};
:: endif

@try:
use schema {{DBS}};

alter session set timezone = 'America/New_York';
-- alter session set timezone = 'UTC';

-- alter session set timestamp_ltz_output_format = 'YYYY-MM-DD HH24:MI:SS.FF3';

alter session set transaction_abort_on_error = true;

-----------------------------------------------------------------
-- DONE
-----------------------------------------------------------------

# Running

To Run using the "settings.ys.json" settings file:
```
run ys
run jj
run live
```

To run with "settings.live.json" for 20180102
```
run ys 20180102
run jj 20180102
run live 20180102
```





# General 

- Files in SQL folder will be executed in alphanumeric order
- Scripts with a "Ticker Query" will be exected once for each ticker




# `settings.json` 

- It os OK to create new settings files any time
- To use `settings.XYZ.json`, your do: run `XYZ`
- See settings.live.json for setting descriptions
- Keys starting with slashes are comments




# SQL Script Substitutions 

- `CUT_DATE` --> Current cut_date (like 20180208)
- `CUT_TABLE` --> Current cut_table (like rawdata.moa.v_moa_week_20180208)
- `TEMP` --> temp or '' depending on settings files
- `FOUNDATION` --> `setting.foundation_schema` setting
- `STAGE` --> `setting.stage_schema` setting







# Dynamic SQL

## Rules

- Dynamic SQL stars with `-- DYNAMIC SQL BEGIN --`
- And ends with `-- DYNAMIC SQL BEGIN --`
- Single quotes in output have to be escaped (`''` or `\'`)
- Or [dollar quoted](https://docs.snowflake.net/manuals/sql-reference/data-types-text.html#dollar-quoted-string-constants)
- Columns will be concatenated (with no separating space)
- Rows will have a new-line appended and then concatenated into a block of text


## Example 1

This...
```
-- DYNAMIC SQL BEGIN --
select $$select 1, 2, 'a', $$ || seq4() || ';'
from table(generator(rowcount => 3));
-- DYNAMIC SQL END --

```

Outputs this...
```
-- GENERATED SQL BEGIN --

-- 
-- select $$select 1, 2, 'a', $$ || seq4() || ';'
-- from table(generator(rowcount => 10));
-- 

select 1, 2, 'a', 0;
select 1, 2, 'a', 1;
select 1, 2, 'a', 2;
;

-- GENERATED SQL END --

```

## Example 2

This...
```
-- DYNAMIC SQL BEGIN --
select 'select 1, 2, ''a'', ' || seq4() || ', ' || $$'TICKER';$$
from table(generator(rowcount => 10));
-- DYNAMIC SQL END --
```
Outputs this...
```
-- GENERATED SQL BEGIN --

-- 
-- select 'select 1, 2, ''a'', ' || seq4() || ', ' || $$'ABMD';$$
-- from table(generator(rowcount => 3));
-- 

select 1, 2, 'a', 0, 'ABMD';
select 1, 2, 'a', 1, 'ABMD';
select 1, 2, 'a', 2, 'ABMD';
;

-- GENERATED SQL END --
```








# Ticker Query

If a SQL file contains this line:
```
Tickers: select $1 from foundation.foundation_mfg_list
```

Then the file will be exected once for each ticker specified by this query.  This allows each SQL file to specify queries.






# Tips
- Avoid hard coded schemas
- References to `FOUNDATION` and `STAGE` schemas should be in all-caps in order to dynamically updated
- `MOA_LIVE.FOUNDATION` needs to be periodically re-cloned 






# Viewing this Document is VS Code

- View -- Ctrl-Shift-V
- Side by Side -- Ctrl-K V
- [More info](https://code.visualstudio.com/docs/languages/markdown)
- [Markdown Cheat Sheet](http://commonmark.org/help/)


# Packages

conda install -c anaconda boto3
pip install --upgrade snowflake-connector-python
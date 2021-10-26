# GP2 Runner

## Jinja
- Template Designer: https://jinja.palletsprojects.com/en/2.11.x/templates/

## Built in Variables
- `last_fetch`
    - Default value: `[]`
    - Type: List
    - List of rows from last fetch
    - Usage: Access rows after
- `settings`:
    - Value: Dictionary of settings read from JSON, initialized on startup
    - Type: Dictionary
    - Example: `{{settings.database}}` to access database setting
- `start_time`:
    - Value: `gp2.job.start_time`
    - Type: Datetime
- `run_date`:
    - Value: `gp2.job.start_time.date()`
    - Type: Date
- `run_id`
    - Value: `gp2.job.run_id`
    - Type: Int
- `git_hash`:
    - Value: `gp2.job.git_hash`
    - Type: string
- `job_output_url`:
    - The URL where the an archive of the job output files can be accessed
    - Value: `gp2.job.job_output_locations.output_url`
    - Type: string
- `cwd`:
    - Value: `os.getcwd()`
    - Type: String

# Pandas Objects and Functions

- `pandas`:
    - Value: `pandas` module
    - Type: Python Module
- `get_excel_dataframe`:
    - Value: `gp2.utils.dataframe.get_excel_dataframe`
    - Type: Function
- `get_csv_dataframe`:
    - Value: `gp2.utils.dataframe.get_csv_dataframe`
    - Type: Function

# Result-set in Functions

- Optional Argument `sql`:
    - Default: `"select * from table(result_scan(last_query_id()))"`
- Returns: Snowflake result-set (list of lists)
- `fetch_all(sql) -> list[list]`:


# SimpleNamespace Result-set in Functions

- Optional Argument
    - `sql`:`"select * from table(result_scan(last_query_id()))"`
- Returns
    - Result-set from last query, as list of `SimpleNamespace` objects
- Variations
    - `fetch_all_simple(sql:str) -> list[SimpleNamespace]`
        - Returns all rows
    - `fetch_many_simple(sql:str, n) -> [SimpleNamespace]`
        - Returns n rows
    - `fetch_one_simple(sql:str) -> SimpleNamespace`
        - Returns first row

# Single Value Result Function
- Function: `fetch_value(sql:str) -> any`
- Default Argument
    - Name: `sql`
    - Default Value: `"select * from table(result_scan(last_query_id()))"`
- Returns: First row of first column

# Log Functions

- `log_debug(msg:str) -> str`
- `log_info(msg:str) -> str`
- `log_warning(msg:str) -> str`
- `log_error(msg:str) -> str`


# Assert Functions

- `assert_helper(test:bool, msg:str)`
- `raise_helper(msg)`

# Filter Functions

- `comment_lines(s)`
- `trim_lines(s)`
- `condense_whitespace(s)`
- `format_date(d, format=r'%Y-%m-%d')`
- `format_datetime(d, format=r'%Y-%m-%d %H:%M')`
- `strip(str) -> str`



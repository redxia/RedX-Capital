# Changes in gp2

* Linux Compatibility
    * Tested in containers running AmazonLinux 2.0
* Refactored Python Framework
    * Simplified and more modulear
* Settings
    * Settings folder
    * Default settings files -- `settings.default.json`
    * Shared settings files
    * Global settings file -- `da.main\Job\shared\gp2\settings\settings.default.json`
    * Simplified error message for malformed settings files
* Logs
    * Logs folder
    * Specify file/folder names in settings
* Temp Folder
    * Specify folder name in settings
    * Folder no longer deleted, just files
* Runner
    * Undefined variables default to raising an error -- Can override in settings (`jinja_strict_undefined` - true/false)
    * Faster -- Skips blank queries by removing comments
    * Shared and global Jinja modules, macros, templates
        * csv_load, csv_unload
        * init, state
        * html template
    * Built-in steps
        * `gp2/runner/steps/system_step_1_initialize.sql` -- Sets current role, warehouse, database, schema, TZ; initializes DATABASE, SCHEMA, DBS
        * `gp2/runner/steps/system_step_2_initial_state.sql` -- Logs initial state
        * `gp2/runner/steps/system_step_3_finish_state.sql` -- Logs finish state
    * Removed multi-threading, which was not in use -- Will replace with async queries when supported
    * Step folder-names included in output filename
    * Python steps no longer export everything (including modules) -- only items `exports` dictionary, if specified
    * Python steps now have access to vars in previous step -- via `run(vars)` method
    * [Jinja Extensions](https://jinja.palletsprojects.com/en/2.11.x/templates/#extensions) added:
        * Expression Statements: `:: do log_info('Important message')`
        * Loop controls: `break` and `continue`
        * With statements: Providing local variable scope

* Job
    * Displays output URL
    * Faster -- Uploads minimal info
    * Eliminate singleton check
    * Support for running multiple jobs concurrently (by specifying different log files and tmp folders in each instance's settings file)

# Breaking Changes

* Settings files in settings folder
* In SQL steps, expressions like `{{ log_info('...') }}` should now be change to `-- {{ log_info('...') }}` to avoid being interpreted as part of a SQL expression
* TMP_DIR moved to settings.TMP_DIR
* py_step global variables no longer available in SQL -- used explicit `export` dictionary, or return a dictionary from run()

# Environment Variables

```
SNOWSQL_USER=
SNOWSQL_PWD=****
PYTHONPATH=c:\dev\da.etl\;c:\dev\da.main\Job\shared\
PYLINTRC=c:\dev\da.main\.pylintrc
```

# Requirements

**Python 3.8.8**

```
pip install -r gp2/requirements.txt
```

# KNOWN ISSUES

* **BUG**: Special chars cause utils.append_file() to raise exception.
    * **Possible fix**: Use UTF8 files by default?
    * **Status**: Has not happened recently

* **ISSUE**: Snowflake.format_rows() runs out of memory
    * **Current Workaround**: Truncate to 1000 lines by default.  Override in settings with format_rows_max_lines, if present.
    * **Alternative**: May be more efficient to write the output as it's generated, rather than holding it in memory


# TODOS

* **FEATURE**: Async queries (when available)

* **FEATURE**: Unit testing

# Example Usage

* Assumptions
    * Current working directory contains project files (i.e. settings, steps, tmp, output folders)

* Windows
    1. `run.bat stage`
    1. `python main.py stage` or `python -m gp2.runner.run stage`

* Windows + Docker
    1. `set path=%path%;\dev\da.main\job\shared\scripts\` to add sripts folder to path
    1. `docker_run` (or `docker_run_py37` or `docker_run_py38`) to start with bash and manually run job
    1. `docker_run stage` (or `docker_run_py37 stage` or `docker_run_py38 stage`) to start container and run job with `stage` settings



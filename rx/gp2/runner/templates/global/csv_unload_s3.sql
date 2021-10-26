
:: macro csv_unload_s3(
        stage, 
        table=None, 
        select=None, 
        delimiter=',', 
        compression='gzip', 
        header=true,
        single=true) 

    --------------------------------------------------------------------------------------------------
    -- {{ log_info('CSV_UNLOAD_S3: %s --> %s' % (table, stage)) }}
    --------------------------------------------------------------------------------------------------

    -- {{ assert(table or select, 'table and select args cannot both be empty') }}
    -- {{ assert(stage, 'stage cannot be empty') }}

    :: if select
        :: set from = '(\n' + select + '\n)\n'
    :: else
        :: set from = table
    :: endif

    list {{stage}};

    copy into {{stage}}
    from {{from}}
    file_format = (
        type = csv 
        compression={{compression}} 
        field_delimiter='{{delimiter}}' 
        null_if=('NULL','')
        empty_field_as_null=true 
        field_optionally_enclosed_by='"' 
        encoding='utf8'
    )
	overwrite = true 
	header = {{header}} 
	single = {{single}}
	max_file_size = 5368709120;
    ;

    list {{stage}};

    --------------------------------------------------------------------------------------------------
    -- CSV_UNLOAD_S3: COMPLETE
    --------------------------------------------------------------------------------------------------

:: endmacro 



:: macro csv_unload(table=None, select=None, filename=None, folder='tmp', delimiter=',', compression='none', header=true) 

    :: if not filename
        :: set filename = table + '.csv'
    :: endif

    --------------------------------------------------------------------------------------------------
    -- {{ log_info('CSV_UNLOAD: %s/%s' % (folder, filename)) }}
    --------------------------------------------------------------------------------------------------

    -- {{ assert(table or select, 'table and select args cannot both be empty') }}
    -- {{ assert(table or filename, 'table and filename args cannot both be empty') }}

    :: set stage|strip
        @~/{{run_id}}/{{filename}}
    :: endset

    remove {{stage}};

    :: if select
        :: set from = '(\n' + select + '\n)\n'
    :: else
        :: set from = table
    :: endif

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
	single = true
	max_file_size = 5368709120;
    ;

    list {{stage}};

    get {{stage}} 'file://{{folder}}';

    remove {{stage}};

    --------------------------------------------------------------------------------------------------
    -- CSV_UNLOAD COMPLETE
    --------------------------------------------------------------------------------------------------

:: endmacro 


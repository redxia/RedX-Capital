


:: macro csv_load(filename, table, delimiter=',', compression='auto_detect', skip_header=1) 

    --------------------------------------------------------------------------------------------------
    -- {{ log_info('CSV_LOAD START: %s --> %s' % (filename, table)) }}
    --------------------------------------------------------------------------------------------------

    {% set stage|strip -%}
        @%{{table}}/load/
    {%- endset %}
    
    remove {{stage}};

    put 'file://{{filename}}' {{stage}} 
        source_compression={{compression}} 
        overwrite=true;

    list {{stage}};

    copy into {{table}} 
    from {{stage}}
    file_format = (
        type = csv 
        compression=auto 
        field_delimiter='{{delimiter}}' 
        -- record_delimiter='\r\n'
        skip_header={{skip_header}} 
        null_if=('NULL','')
        empty_field_as_null=true 
        field_optionally_enclosed_by='"' 
        encoding='utf8'
    )
    -- validation_mode = RETURN_ALL_ERRORS 
    ;

    remove {{stage}};

    --------------------------------------------------------------------------------------------------
    -- CSV_LOAD COMPLETE
    --------------------------------------------------------------------------------------------------

:: endmacro 


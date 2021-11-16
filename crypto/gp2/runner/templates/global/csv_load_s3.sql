:: macro csv_load_s3(
        stage, 
        table, 
        delimiter=',', 
        compression='none', 
        skip_header=1,
        date_format='auto',
        timestamp_format='auto',
        encoding='UTF8',
        max_skip_rows=1000,
        order_by="1,2,3", 
        PK=None,
        temp=false
    ) 

    --------------------------------------------------------------------------------------------------
    -- {{ log_info('CSV_LOAD_S3 START: %s --> %s' % (stage, table)) }}
    --------------------------------------------------------------------------------------------------

    -- List files that will be loaded, for debugging
    list '{{stage}}';

    -- Load 'em
    copy into {{table}}
    from '{{stage}}'
    file_format = ( 
        type = 'csv' 
        compression=auto 
        field_delimiter = '{{delimiter}}' 
        --record_delimiter = '\r\n' 
        skip_header = {{skip_header}}
        --field_optionally_enclosed_by = '"' 
        trim_space = true 
        --error_on_column_count_mismatch = false 
        --escape = 'none' 
        --escape_unenclosed_field = '\134'
        escape_unenclosed_field = none 
        date_format = '{{date_format}}' 
        timestamp_format = '{{timestamp_format}}'
        null_if = ('\000', 'NULL', '\\\\N', 'null', '\\N','')
        empty_field_as_null = true
        replace_invalid_characters =true
        validate_utf8 = true
        encoding = '{{encoding}}'
    )
    on_error = skip_file_{{max_skip_rows}}
    -- validation_mode = return_10_rows
    ;

    :: set TEMP = 'TEMP' if temp else ''

    -- Save load errors
    create or replace {{TEMP}} table {{table}}_errors as
    select * from table(validate({{table}}, job_id => '_last'));

    -- Save load log
    create or replace {{TEMP}} table {{table}}_load as
    select * from table(result_scan(-2));

    -- Sort in place
    :: if order_by
        insert overwrite into {{table}}
        select * from {{table}}
        order by {{order_by}};
    :: endif

    -- Create and validate primary key
    :: if PK
        alter table {{table}} add primary key ({{PK}}); 
        call shared.qa.assert_pk_valid('{{table}}','{{PK}}')
    :: endif

    --------------------------------------------------------------------------------------------------
    -- CSV_LOAD_S3 COMPLETE
    --------------------------------------------------------------------------------------------------

:: endmacro 




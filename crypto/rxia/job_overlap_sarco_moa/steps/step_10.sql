
-- :: set DATES = fetch_all_simple("""select distinct(last_day(date)) as date 
--         from sarco_live.merged.v_sarco_moa_current where source = 'PETREL' order by date""")
:: set DATES = fetch_all_simple("""select distinct(last_day(date)) as date from 
        temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where source ilike 'sarco' order by date""")
--        from sarco_live.merged.v_sarco_moa_current 
:: set DATES_SIZE = DATES|length


create or replace table spend_overlap (moa_fac_id varchar, sarco_fac_id varchar, match_spend float, total_spend float, spend_overlap float, date date);

:: for i in range(DATES_SIZE)
    :: if (i+5 <= DATES_SIZE-1) and (i % 3 == 0)
        :: set DATE1 = DATES[i+0].DATE
        :: set DATE2 = DATES[i+1].DATE
        :: set DATE3 = DATES[i+2].DATE
        :: set DATE4 = DATES[i+3].DATE
        :: set DATE5 = DATES[i+4].DATE
        :: set DATE6 = DATES[i+5].DATE

        create or replace table sku_overlap as
        select a.fac_id as moa_fac_id, b.fac_id as sarco_fac_id, a.sku, a.m1, a.m2, a.m3, a.m4, a.m5, a.m6 from
            (select fac_id, sku, ifnull(m1, 0) as m1, ifnull(m2, 0) as m2, ifnull(m3, 0) as m3, ifnull(m4, 0) as m4, ifnull(m5, 0) as m5, ifnull(m6, 0) as m6 
            from
                (select facility_id, concat(ifnull(ltrim(mfg_ticker,0), ''), mfg_catalog) as ticker_sku, last_day(date) as month_end, sum(total_spend) as total_spend
                --from sarco_live.merged.v_sarco_moa_current 
                from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION
                where month_end >= '{{DATE1}}' 
                and month_end <= '{{DATE6}}' 
                and source ilike 'MOA' 
                and facility_id != 'AGGREGATED'
                and total_spend > 0
                and mfg_catalog != 'UNKNOWN'
                and mfg_catalog is not NULL
                group by 1, 2, 3)
            pivot (sum(total_spend) for month_end in ('{{DATE1}}','{{DATE2}}','{{DATE3}}','{{DATE4}}','{{DATE5}}','{{DATE6}}')) as p 
            (fac_id, sku, m1, m2, m3, m4, m5, m6)) as a
        inner join
            (select fac_id, sku, ifnull(m1, 0) as m1, ifnull(m2, 0) as m2, ifnull(m3, 0) as m3, ifnull(m4, 0) as m4, ifnull(m5, 0) as m5, ifnull(m6, 0) as m6 
            from
                (select facility_id, concat(ifnull(mfg_ticker, ''), mfg_catalog) as ticker_sku, last_day(date) as month_end, sum(total_spend) as total_spend
                --from sarco_live.merged.v_sarco_moa_current 
                from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION
                where month_end >= '{{DATE1}}' 
                and month_end <= '{{DATE6}}' 
                and source ilike 'sarco' 
                and facility_id != 'AGGREGATED'
                and total_spend > 0
                and mfg_catalog != 'UNKNOWN'
                and mfg_catalog is not NULL
                group by 1, 2, 3)
            pivot (sum(total_spend) for month_end in ('{{DATE1}}','{{DATE2}}','{{DATE3}}','{{DATE4}}','{{DATE5}}','{{DATE6}}')) as p 
            (fac_id, sku, m1, m2, m3, m4, m5, m6)) as b
        on a.sku = b.sku
        and a.m1 = b.m1
        and a.m2 = b.m2
        and a.m3 = b.m3
        and a.m4 = b.m4
        and a.m5 = b.m5
        and a.m6 = b.m6
        order by 1, 2;

        create or replace table facility_total_spend as
        select facility_id as moa_fac_id, sum(total_spend) as total_spend
        --from sarco_live.merged.v_sarco_moa_current
        from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION
        where last_day(date) >= '{{DATE1}}' 
        and last_day(date) <= '{{DATE6}}' 
        and source = 'MOA' 
        and facility_id != 'AGGREGATED'
        and total_spend > 0
        and mfg_catalog != 'UNKNOWN'
        and mfg_catalog is not NULL
        group by 1;

        create or replace table facility_match_spend as
        select moa_fac_id, sarco_fac_id, sum(m1) + sum(m2) + sum(m3) + sum(m4) + sum(m5) + sum(m6) as total_spend
        from sku_overlap
        group by 1, 2;



        create or replace table spend_overlap_p as
        select a.moa_fac_id, a.sarco_fac_id, a.total_spend as match_spend, b.total_spend as total_spend, 100*a.total_spend/b.total_spend as spend_overlap, '{{DATE6}}'::date as date from
        (facility_match_spend) as a
        left join
        (facility_total_spend) as b
        on a.moa_fac_id = b.moa_fac_id
        where spend_overlap > 1;



        insert into spend_overlap(moa_fac_id, sarco_fac_id, match_spend, total_spend, spend_overlap, date)
        select moa_fac_id, sarco_fac_id, match_spend, total_spend, spend_overlap, date from spend_overlap_p;

    
    :: endif

:: endfor

--select * from from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION limit 10000;

use schema research.rxia;

create or replace table facility_match_1 as
select source, date, year(date) year, quarter(date) quarter, ltrim(facility_id,0) as facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog, sum(total_spend)::decimal(20,2) as monthly_spend, sum(volume)::int as monthly_volume from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION
group by 1, 2, 3, 4, 5, 6, 7, 8, 9;

--select * from facility_match_1 limit 10000;

-- create or replace table facility_match_2 as
-- select source, date, year, quarter, facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog, monthly_spend, monthly_volume, 
-- count(*) over (partition by facility_id, mfg_catalog, year, quarter) months_spend,
-- hash_agg(date, mfg_catalog, monthly_spend) over (partition by facility_id, mfg_catalog, year, quarter) as q_sku_hash
-- from facility_match_1;


create or replace table facility_match_2 as
select source, date, year, quarter, facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog, monthly_spend, monthly_volume, 
count(*) over (partition by facility_type, bed_size, mfg_catalog, year, quarter) months_spend,
hash_agg(date, mfg_catalog, monthly_spend) over (partition by facility_type, bed_size, mfg_catalog, year, quarter) as q_sku_hash
from facility_match_1;

--select * from facility_match_2 order by source, year, quarter, facility_id, mfg_catalog, date limit 1000;


create or replace table facility_match_3 as
select source, year, quarter, facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog, sum(monthly_spend) as quarterly_spend, sum(monthly_volume) as quarterly_volume, any_value(q_sku_hash) as q_sku_hash
from facility_match_2 where months_spend >= 3
group by source, year, quarter, facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog;

--select * from facility_match_3 order by source, year, quarter, facility_id, mfg_catalog limit 1000;



create or replace table facility_match_4 as
select a.year, a.quarter, a.facility_id facility_id_moa, a.facility_type facility_type_moa, a.bed_size bed_size_moa,
b.facility_id facility_id_sarco, b.facility_type facility_type_sarco, b.bed_size bed_size_sarco,
a.mfg_ticker ticker_moa, b.mfg_ticker ticker_sarco, 
a.mfg_catalog, a.quarterly_spend, a.quarterly_volume quarterly_volume_moa, b.quarterly_volume quarterly_volume_sarco from
(select * from facility_match_3 where source = 'MOA') as a
inner join
(select * from facility_match_3 where source = 'SARCO') as b
on a.q_sku_hash = b.q_sku_hash;

--select * from facility_match_4 order by year, quarter, facility_id_moa, facility_id_sarco, mfg_catalog limit 10000;

-- double check if this requires a matching over facility type and bed size instead of facility id

create or replace table facility_match_4b as
with a as
(select facility_id_moa, facility_id_sarco, mfg_catalog, count(*) over (partition by facility_id_moa, facility_id_sarco, mfg_catalog) as sku_quarter_matches 
from facility_match_4)
select facility_id_moa, facility_id_sarco,  mfg_catalog, any_value(sku_quarter_matches) as sku_quarter_matches 
from a group by 1, 2, 3;

create or replace table facility_match_4c as
select facility_id_moa, facility_id_sarco, avg(sku_quarter_matches) as avg_quarters_per_sku
from facility_match_4b group by 1, 2;

--select * from facility_match_4c order by 1, 2;


create or replace table facility_match_5 as
select year, quarter, facility_id_moa, facility_type_moa, bed_size_moa, facility_id_sarco, facility_type_sarco, bed_size_sarco, count(*) as matches
from facility_match_4 group by 1, 2, 3, 4, 5, 6, 7, 8;

--select * from facility_match_5 order by facility_id_moa, year, quarter, matches limit 1000;


create or replace table facility_match_6 as
select facility_id_moa, facility_type_moa, bed_size_moa, facility_id_sarco, facility_type_sarco, bed_size_sarco, count(*) as quarter_matches, sum(matches) as total_matches
from facility_match_5 group by 1, 2, 3, 4, 5, 6;


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- select division_moa, division_sarco, facility_id_moa, facility_id_sarco, facility_type_moa, facility_type_sarco, bed_size_moa, bed_size_sarco, total_matches 
-- from facility_match_6 order by facility_id_moa, quarter_matches limit 10000;
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

create or replace table facility_match_7 as
select *,
ratio_to_report(total_matches) over (partition by facility_id_moa) as pct_all_sarco_matches,
ratio_to_report(total_matches) over (partition by facility_id_sarco) as pct_all_moa_matches,
total_matches/quarter_matches as avg_skus_per_quarter
from facility_match_6;


create or replace table facility_match_8 as
select a.*, b.avg_quarters_per_sku, a.avg_skus_per_quarter*b.avg_quarters_per_sku as score
from
facility_match_7 as a
left join
facility_match_4c as b
on a.facility_id_moa = b.facility_id_moa
and a.facility_id_sarco = b.facility_id_sarco;

-- select * from facility_match_8 where total_matches > 2 and score > 1 and (pct_all_moa_matches > 0.05 or pct_all_sarco_matches > 0.05) order by facility_id_moa, total_matches;
--where pct > 0.5 and facility_id_sarco not like 'P_AGG%' and matches > 100
;


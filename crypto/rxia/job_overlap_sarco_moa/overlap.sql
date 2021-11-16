select * from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION limit 10000;

use schema temp.rxia;

create or replace table facility_match_1 as
select source, date, year(date) year, quarter(date) quarter, facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog, sum(total_spend)::decimal(20,2) as monthly_spend, sum(volume)::int as monthly_volume from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10;

select * from facility_match_1 limit 10000;



create or replace table facility_match_2 as
select source, date, year, quarter, facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog, monthly_spend, monthly_volume, 
hash_agg(date, mfg_catalog, monthly_spend) over (partition by facility_id, mfg_catalog, year, quarter) as q_sku_hash
from facility_match_1;

select * from facility_match_2 order by source, year, quarter, facility_id, mfg_catalog, date limit 1000;


create or replace table facility_match_3 as
select source, year, quarter, facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog, sum(monthly_spend) as quarterly_spend, sum(monthly_volume) as quarterly_volume, any_value(q_sku_hash) as q_sku_hash
from facility_match_2
group by source, year, quarter, facility_id, facility_type, bed_size, mfg_ticker, mfg_catalog;

select * from facility_match_3 order by source, year, quarter, facility_id, mfg_catalog limit 1000;



create or replace table facility_match_4 as
select a.year, a.quarter,  
a.facility_id facility_id_moa, a.facility_type facility_type_moa, a.bed_size bed_size_moa,
b.facility_id facility_id_sarco, b.facility_type facility_type_sarco, b.bed_size bed_size_sarco,
a.mfg_ticker ticker_moa, b.mfg_ticker ticker_sarco, 
a.mfg_catalog, a.quarterly_spend, a.quarterly_volume quarterly_volume_moa, b.quarterly_volume quarterly_volume_sarco from
(select * from facility_match_3 where source = 'MOA') as a
inner join
(select * from facility_match_3 where source = 'SARCO') as b
on a.q_sku_hash = b.q_sku_hash;

select * from facility_match_4 limit 10000;


create or replace table facility_match_5 as
select facility_id_moa, facility_type_moa, bed_size_moa, facility_id_sarco, facility_type_sarco, bed_size_sarco, count(*) as matches from facility_match_4 group by 1, 2, 3, 4, 5, 6;

select * from facility_match_5 order by facility_id_moa, matches;


create or replace table facility_match_6 as
select *, ratio_to_report(matches) over (partition by facility_id_moa) as pct from facility_match_5;

select * from facility_match_6 where pct > 0.5 and facility_id_sarco not like 'S_AGG%' and matches > 100;


select ifnull(a.date, b.date) date, ifnull(a.mfg_ticker, b.mfg_ticker) mfg_ticker, ifnull(a.mfg_catalog, b.mfg_catalog) mfg_catalog, a.spend_moa, b.spend_sarco, ifnull(a.spend_moa, b.spend_sarco) common, a.descr desc_moa, b.descr desc_sarco from
(select date, ifnull(mfg_ticker, '_') mfg_ticker, mfg_catalog, any_value(source_description) descr, sum(total_spend) as spend_moa from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'M_0000004792' and date > '2016-01-01' group by 1, 2, 3) as a
full outer join
(select date, ifnull(mfg_ticker, '_') mfg_ticker, mfg_catalog, any_value(source_description) descr, sum(total_spend) as spend_sarco from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'S_0000064931' and date > '2016-01-01' group by 1, 2, 3) as b
on a.date = b.date
and a.mfg_ticker = b.mfg_ticker
and a.mfg_catalog = b.mfg_catalog;

select * from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'P_0000030974' and date = '2016-10-31';


select a.date, a.spend spend_moa, b.spend spend_sarco from
(select date, sum(total_spend) spend from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'M_0000004792' group by 1) as a
full outer join
(select date, sum(total_spend) spend from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'S_0000064931' group by 1) as b
on a.date = b.date
order by date;




select date, sum(total_spend) spend from
(select b.date, b.total_spend from
(SARCO.MONITOR_MAPPING.V_KNEE_MAPPING_CURRENT) as a
left join
(select * from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'M_0000004792') as b
on a.mfg_ticker = b.mfg_ticker
and a.mfg_catalog = b.mfg_catalog)
group by 1;



select a.date, a.spend spend_moa, b.spend spend_sarco from
  (select date, sum(total_spend) spend from
  (select b.date, b.total_spend from
  (SARCO.MONITOR_MAPPING.V_KNEE_MAPPING_CURRENT) as a
  left join
  (select * from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'M_0000004792') as b
  on a.mfg_ticker = b.mfg_ticker
  and a.mfg_catalog = b.mfg_catalog)
  group by 1) 
as a
full outer join
  (select date, sum(total_spend) spend from
  (select b.date, b.total_spend from
  (SARCO.MONITOR_MAPPING.V_KNEE_MAPPING_CURRENT) as a
  left join
  (select * from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'P_0000064931') as b
  on a.mfg_ticker = b.mfg_ticker
  and a.mfg_catalog = b.mfg_catalog)
  group by 1)  
as b
on a.date = b.date
order by date;

create or replace table top_skus as
with a as
(select facility_id, date, mfg_ticker, mfg_catalog, sum(total_spend) spend 
from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id = 'M_0000004792' and mfg_ticker = 'JNJ' group by 1, 2, 3, 4)
select facility_id, mfg_ticker, mfg_catalog, count(spend) top_skus from a group by 1, 2, 3 order by 4 desc
limit 25;

select * from top_skus;

select date, facility_id, mfg_ticker, mfg_catalog, sum(total_spend) total_spend from
(select b.* from
top_skus as a
left join
(select * from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id in ('M_0000004792', 'P_0000064931')) as b
on a.mfg_ticker = b.mfg_ticker
and a.mfg_catalog = b.mfg_catalog)
group by 1, 2, 3, 4
order by 1, 2, 3, 4;


select a.date, a.mfg_catalog, a.total_spend from
(select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id in ('M_0000004792') group by 1, 2) as a
inner join
(select date, mfg_catalog, sum(total_spend) as total_spend from temp.sarco_test.SARCO_20210812_MOA_20210812_GUDID_20210801_UNION where facility_id in ('P_0000064931') group by 1, 2) as b
on a.date = b.date
and a.mfg_catalog = b.mfg_catalog
and a.total_spend = b.total_spend
limit 1000;

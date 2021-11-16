

-- Details: This script creates the 12_03 summary table
-- Parameters: Cut date and Ticker needs to be changed for every tables
-- Section 1 need to change the s query of the <
-- Section 2 need to change the facility to include or not to include, include or exclude same stores
-- Section 3 No changes

-- Section 1
create or replace table estimator_12_01_CSII_global_facility_count_20170727_rx as
with
t as(
select
facility_id as FacilityID,
sum(total_spend) as total_spend
from runner_10_cleaned_base_table
group by 1
),
s as(
select
*,
case
when datediff(day,dateadd(month,1,gp_transaction_date::date), (left('20170727',4)|| '-' || left(right('20170727',4),2) || '-' || right('20170727',2))::date) < 06  then 'Flag' -- use the day after if it includes an extra month. default 6
else null
end flag
from runner_10_cleaned_base_table
where facility_id in (select FacilityID from t where total_spend > 100000)
)
select
gp_transaction_date as transaction_date,
count(distinct facility_id) as facility_count
from s
where flag is null
group by 1;
-- 0:00:03.765353
-- 01a01122-0502-e9eb-0000-0f7505f332fe
-- Table ESTIMATOR_12_01_CSII_GLOBAL_FACILITY_COUNT_20170727_RX successfully created.

--Section 2
--Ticker specific panel
--manufacturer facility count by date
--facilities over 100000 in total spend
create or replace table estimator_12_02_CSII_manufacturer_facility_count_20170727_rx as
with
t as(
select
facility_id as FacilityID,
sum(total_spend) as total_spend
from runner_10_cleaned_base_table
group by 1
),
a as (
select *
from runner_11_05_CSII_aggregation_20170727
---where flag is null
)
select
transaction_date,
sum(total_spend)/count(distinct facilityid) as avg_facility_spend,
count(distinct facilityid)                  as facility_count,
sum(total_spend)                            as total_spend
from a
where (facilityid
in (select facilityid from t where total_spend > 100000))
---- COMMENT BELOW TO REMOVE SAME STORE
and (facilityid in (select facility_id from estimator_12_00_all_moa_same_store_20170727))
group by 1;
-- 0:00:02.039428
-- 01a01122-0502-e9eb-0000-0f7505f33302
-- Table ESTIMATOR_12_02_CSII_MANUFACTURER_FACILITY_COUNT_20170727_RX successfully created.

-- Section 3
--factor creation
create or replace table estimator_12_03_CSII_factor_20170727_rx as
select
a.transaction_date                                      as gp_transaction_date,
a.facility_count                                        as panel_facility_cnt,
5100/a.facility_count                                   as facility_factor,
b.avg_facility_spend,
b.facility_count                                        as company_facility_count,
b.total_spend,
(5100/a.facility_count)*b.facility_count                as company_factor,
row_number() over (order by a.transaction_date asc)     as date_cnt,
row_number() over (order by a.transaction_date desc) as months_from_current
from estimator_12_01_CSII_global_facility_count_20170727_rx as a
left join estimator_12_02_CSII_manufacturer_facility_count_20170727_rx as b
on a.transaction_date = b.transaction_date
--where gp_transaction_date <> '2020-01-01' -- comment this out. case by case
order by gp_transaction_date;
-- 0:00:01.942701
-- 01a01122-0502-e9eb-0000-0f7505f33306
-- Table ESTIMATOR_12_03_CSII_FACTOR_20170727_RX successfully created.


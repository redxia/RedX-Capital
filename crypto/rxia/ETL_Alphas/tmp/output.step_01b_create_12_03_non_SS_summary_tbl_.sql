

-- Details: This script creates the 12_03 summary table
-- Parameters: Cut date and Ticker needs to be changed for every tables
-- Section 2 need to change the facility to include or not to include, include or exclude same stores
-- Section 3 No changes

--Section 2
--Ticker specific panel
--manufacturer facility count by date
--facilities over 100000 in total spend
create or replace table estimator_12_02_CSII_manufacturer_facility_count_20170727_non_SS_rx as
with
t as(
select
facility_id         as FacilityID,
sum(total_spend)    as total_spend
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
sum(total_spend)/count(distinct facilityid)     as avg_facility_spend,
count(distinct facilityid)                      as facility_count,
sum(total_spend)                                as total_spend
from a
where (facilityid in (select facilityid from t where total_spend > 100000))
---- COMMENT BELOW TO REMOVE SAME STORE
--and (facilityid in (select facility_id from estimator_12_00_all_moa_same_store_20170727))
group by 1;
-- 0:00:06.081650
-- 01a01122-0502-e9ac-0000-0f7505f328f6
-- Table ESTIMATOR_12_02_CSII_MANUFACTURER_FACILITY_COUNT_20170727_NON_SS_RX successfully created.

-- Section 3
--factor creation
create or replace table estimator_12_03_CSII_factor_20170727_non_SS_rx as
select
a.transaction_date                                      as gp_transaction_date,
a.facility_count                                        as panel_facility_cnt,
5100/a.facility_count                                   as facility_factor,
b.avg_facility_spend,
b.facility_count                                        as company_facility_count,
b.total_spend,
(5100/a.facility_count)*b.facility_count                as company_factor,
row_number() over (order by a.transaction_date asc)     as date_cnt,
row_number() over (order by a.transaction_date desc)    as months_from_current
from estimator_12_01_CSII_global_facility_count_20170727_rx as a
left join estimator_12_02_CSII_manufacturer_facility_count_20170727_non_SS_rx as b
on a.transaction_date = b.transaction_date
--where gp_transaction_date <> '2020-01-01' -- comment this out. case by case
order by gp_transaction_date;
-- 0:00:01.596919
-- 01a01122-0502-e983-0000-0f7505f2edde
-- Table ESTIMATOR_12_03_CSII_FACTOR_20170727_NON_SS_RX successfully created.


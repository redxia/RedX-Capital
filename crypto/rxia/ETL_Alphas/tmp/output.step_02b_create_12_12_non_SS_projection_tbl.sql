

-- Details: This script creates the 12_12 projection table from 12_03 table
-- Parameters: Cut date and Ticker needs to be changed for every tables

------------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_04_CSII_panel_20170727_non_SS_rx
--monthly estimate -- Removes factors for last 3 months
------------------------------------------------------------------------------------------------
create or replace transient table estimator_12_04_CSII_panel_20170727_non_SS_rx as
with
t as(
select
*,
case
when months_from_current < 4 then 1
else null
end flag
from estimator_12_03_CSII_factor_20170727_non_SS_rx
where flag is null
order by months_from_current asc
LIMIT 15
)
select
gp_transaction_date,
date_cnt                    as x_date_cnt,
company_factor              as y_facility_share,
date_cnt*date_cnt           as x2_date,
date_cnt*company_factor     as xy_date_share
from t
order by gp_transaction_date asc;
-- 0:00:05.136742
-- 01a01123-0502-e983-0000-0f7505f2edea
-- Table ESTIMATOR_12_04_CSII_PANEL_20170727_NON_SS_RX successfully created.

------------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_05_CSII_summations_20170727_non_SS_rx
--Linear Regression
------------------------------------------------------------------------------------------------
create or replace transient table estimator_12_05_CSII_summations_20170727_non_SS_rx as
select
count(*)                as n,
sum(x_date_cnt)         as sum_x,
sum(y_facility_share)   as sum_y,
sum(x2_date)            as sum_x2,
sum(xy_date_share)      as sum_xy
from estimator_12_04_CSII_panel_20170727_non_SS_rx;
-- 0:00:01.384826
-- 01a01123-0502-e8ec-0000-0f7505f31d2a
-- Table ESTIMATOR_12_05_CSII_SUMMATIONS_20170727_NON_SS_RX successfully created.

------------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_06_CSII_slope_20170727_non_SS_rx
------------------------------------------------------------------------------------------------

create or replace transient table estimator_12_06_CSII_slope_20170727_non_SS_rx as
select (n*sum_xy - sum_x*sum_y)/(n*sum_x2-(sum_x*sum_x)) as slope
from estimator_12_05_CSII_summations_20170727_non_SS_rx;
-- 0:00:03.028781
-- 01a01123-0502-e983-0000-0f7505f2edee
-- Table ESTIMATOR_12_06_CSII_SLOPE_20170727_NON_SS_RX successfully created.

------------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_07_CSII_intercept_20170727_non_SS_rx
------------------------------------------------------------------------------------------------
create or replace transient table estimator_12_07_CSII_intercept_20170727_non_SS_rx as
with
t as(
select *
from estimator_12_05_CSII_summations_20170727_non_SS_rx
cross join estimator_12_06_CSII_slope_20170727_non_SS_rx
)
select
*,
(sum_y-slope*sum_x)/n as intercept
from t;
-- 0:00:03.304227
-- 01a01123-0502-e983-0000-0f7505f2edf2
-- Table ESTIMATOR_12_07_CSII_INTERCEPT_20170727_NON_SS_RX successfully created.

------------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_08_CSII_new_factor_20170727_non_SS_rx
------------------------------------------------------------------------------------------------
create or replace transient table estimator_12_08_CSII_new_factor_20170727_non_SS_rx as(
with t as(
select
*,
case
when months_from_current < 4 then 1
else null
end flag
from estimator_12_03_CSII_factor_20170727_non_SS_rx
order by gp_transaction_date asc
),
s as(
select
a.*,
b.slope,
b.intercept
from t as a
left join estimator_12_07_CSII_intercept_20170727_non_SS_rx as b
on flag is not null
)
select
*,
ifnull((slope*date_cnt)+intercept, company_factor) as new_factor
from s
);
-- 0:00:01.749772
-- 01a01123-0502-e9eb-0000-0f7505f3330e
-- Table ESTIMATOR_12_08_CSII_NEW_FACTOR_20170727_NON_SS_RX successfully created.

------------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_09_CSII_quarterly_estimate_20170727_non_SS_rx
--quarterly estimate
------------------------------------------------------------------------------------------------
create or replace transient table estimator_12_09_CSII_quarterly_estimate_20170727_non_SS_rx as
with
t as(
select
case
when 'CSII' ilike 'MDT%' then dateadd(month, -1, gp_transaction_date)
else gp_transaction_date
end new_date,
gp_transaction_date ,
new_factor,
avg_facility_spend
from estimator_12_08_CSII_new_factor_20170727_non_SS_rx
)
select
year(new_date)                                                                          as year,
quarter(new_date)                                                                       as quarter,
listagg(distinct new_date, ',') within group (order by new_date)                        as new_months_agg,
listagg(distinct gp_transaction_date, ',') within group (order by gp_transaction_date)  as old_months_agg,
sum(new_factor*avg_facility_spend)                                                      as quarterly_estimate
from t
group by 1,2
having year >=2012
order by year, quarter;
-- 0:00:01.679617
-- 01a01123-0502-e8d4-0000-0f7505f30b32
-- Table ESTIMATOR_12_09_CSII_QUARTERLY_ESTIMATE_20170727_NON_SS_RX successfully created.

------------------------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_10_CSII_join_official_revenue_20170727_non_SS_rx
--join official revenue
------------------------------------------------------------------------------------------------------------
create or replace transient table estimator_12_10_CSII_join_official_revenue_20170727_non_SS_rx as
with
t as(
select
year,
quarter,
official_revenue,
fiscal_quarter,
'20170727' as cut_date,
reported_date,
estimate
from moa.FOUNDATION_ys.foundations_ticker_revenue_information
where revenue_category = 'CSII'
order by year, quarter
),
s as(
select
max(reported_date) reported_date
from t
where reported_date >= cut_date
and official_revenue is not null
)
select
d.year,
d.quarter,
d.quarterly_estimate::float as quarterly_estimate,
new_months_agg,
old_months_agg,
(
case
when e.official_revenue = 0 then d.quarterly_estimate
when reported_date in (select reported_date from s) then null
else e.official_revenue
end
)::float official_revenue,
fiscal_quarter
from estimator_12_09_CSII_quarterly_estimate_20170727_non_SS_rx as d
left join t as e
on d.year = e.year
and d.quarter = e.quarter;
-- 0:00:01.252150
-- 01a01123-0502-e983-0000-0f7505f2edf6
-- Table ESTIMATOR_12_10_CSII_JOIN_OFFICIAL_REVENUE_20170727_NON_SS_RX successfully created.

--------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_11_CSII_scaling_factor_20170727_non_SS_rx
--scaling factor
------------------------------------------------------------------------------------------
create or replace transient table estimator_12_11_CSII_scaling_factor_20170727_non_SS_rx as
with
n0 as(
select
*,
row_number() over(order by year desc, quarter desc) as rwnumb,
case
when official_revenue is null then 1
else 0
end flag
from estimator_12_10_CSII_join_official_revenue_20170727_non_SS_rx
),
n1 as(
select
year,
quarter,
quarterly_estimate,
case
when rwnumb = 1 and flag = 0 then null
else official_revenue
end official_revenue,
rwnumb,
case
when rwnumb = 1 then 1
when flag = 1 then flag else 0
end flag
from n0
),
n2 as(
select min(rwnumb) as min_numb
from n1 where flag = 0
),
n3 as(
select max(rwnumb) as max_numb
from n1
where rwnumb < (select min_numb from n2)
),
t as(
select
*,
'CSII' as company_name,
row_number() over(order by year desc, quarter desc) as numb
from estimator_12_10_CSII_join_official_revenue_20170727_non_SS_rx
),
s as(
select
sum(quarterly_estimate) as qe_sum
from t
where
case
when company_name = 'CTEC' then numb between 1 + (select max_numb from n3) and 6 + (select max_numb from n3)
when company_name != 'CTEC' then numb between 1 + (select max_numb from n3) and 4 + (select max_numb from n3)
end
),
u as(
select
sum(official_revenue) as or_sum
from t
where
case
when company_name = 'CTEC' then numb between 1 + (select max_numb from n3) and 6 + (select max_numb from n3)
when company_name != 'CTEC' then numb between 1 + (select max_numb from n3) and 4 + (select max_numb from n3)
end
)
select
*,
or_sum/qe_sum as factor
from s
left join u;
-- 0:00:02.860218
-- 01a01123-0502-e9ac-0000-0f7505f32906
-- Table ESTIMATOR_12_11_CSII_SCALING_FACTOR_20170727_NON_SS_RX successfully created.

--------------------------------------------------------------------------------------------
-- CREATE OR REPLACE estimator_12_12_CSII_scaled_estimate_20170727_non_SS_rx
--scaled estimates table
--------------------------------------------------------------------------------------------
create or replace transient table estimator_12_12_CSII_scaled_estimate_20170727_non_SS_rx as
select
a.*,
b.factor,
a.quarterly_estimate*b.factor as scaled_quarterly_estimate
from estimator_12_10_CSII_join_official_revenue_20170727_non_SS_rx as a
left join estimator_12_11_CSII_scaling_factor_20170727_non_SS_rx as b
where 1 = 1;
-- 0:00:03.606672
-- 01a01123-0502-e9ac-0000-0f7505f3290a
-- Table ESTIMATOR_12_12_CSII_SCALED_ESTIMATE_20170727_NON_SS_RX successfully created.

------------------
select
year,
quarter,
official_revenue/1000000,
quarterly_estimate/1000000,
factor,
scaled_quarterly_estimate/1000000,
'CSII',
'20170727'
from estimator_12_12_CSII_scaled_estimate_20170727_non_SS_rx
where year > '2018'
order by 1,2 asc;
-- 0:00:00.434593
-- 01a01123-0502-e8ec-0000-0f7505f31d2e
-- RESULT []

------------------------
-- DONE
------------------------;

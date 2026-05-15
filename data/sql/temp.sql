--show create view dbo.discharge_data_view_demographics;
-- TITLE: Microsoft SQL Server Management Studio
------------------------------

-- Property DefaultSchema is not available for Database '[DOH_AMHD_NO_PII]'. 
-- This property may not exist for this object, or may not be retrievable due to insufficient access rights. 
-- (Microsoft.SqlServer.Smo)
-- For help, click: https://go.microsoft.com/fwlink?ProdName=Microsoft+SQL+Server&ProdVer=16.100.47021.0&EvtSrc=Microsoft.SqlServer.Management.Smo.ExceptionTemplates.PropertyCannotBeRetrievedExceptionText&EvtID=DefaultSchema&LinkId=20476

-- double click on the database to show popup menu
-- select 'Tasks'
-- select 'Import Data'
-- click the 'Next' button
-- for data source, select 'flat file source'
-- click the 'Browse' button
-- at the bottom, change from .txt to .csv
-- select the csv file
-- click the 'Open' button
-- click the 'Next' button
-- for destination, select 'Microsoft OLE DB Provider for SQL Server' (make sure you don't select 'Microsoft OLE DB Driver for SQL Server')
-- enter the server name
-- select 'Use SQL Server Authentication' and provide the username and password

select count(*) from dbo.teds_data_view;

select count(*) from dbo.TEDS_D;
select top 1 * from dbo.TEDS_D;
drop table dbo.TEDS_D;
drop table dbo.TEDS_D_combined_data_Hawaii_2015_2021;
select count(*) from dbo.TEDS_D_combined_data_Hawaii_2015_2021;
-- 126,129

select SERVICES
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by SERVICES;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = 8
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = '8.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = 7
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = '7.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = 6
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = '6.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.services = '2.0';

----
select SERVICES_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by SERVICES_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = 8
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = '8.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = 7
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = '7.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = 6
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = '6.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = '2.0';

-----
select EMPLOY_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by EMPLOY_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = '-9.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = 4
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = '4.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = '1.0';

----

select LIVARAG_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by LIVARAG_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = '-9.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = '1.0';

----

select ARRESTS_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by ARRESTS_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = '-9.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = 0
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = '0.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = '1.0';

----

select DETNLF_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by DETNLF_D;


UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = 9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = '-9.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = 4
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = '4.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = '1.0';

----
-- SUB1_D,SUB2_D,SUB3_D,FREQ1_D,FREQ2_D,FREQ3_D,FREQ_ATND_SELF_HELP_D,SERVSETD

select SUB1_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by SUB1_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 19
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '19.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 18
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '18.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 17
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '17.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 16
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '16.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 13
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '13.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 12
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '12.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 11
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '11.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 10
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '10.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '9.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 7
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '7.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 6
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '6.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 4
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '4.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '1.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = '-9.0';


----
-- SUB1_D,SUB2_D,SUB3_D,FREQ1_D,FREQ2_D,FREQ3_D,FREQ_ATND_SELF_HELP_D,SERVSETD

select SUB2_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by SUB2_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 19
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '19.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 18
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '18.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 17
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '17.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 16
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '16.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 15
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '15.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 14
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '14.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 13
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '13.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 12
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '12.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 11
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '11.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 10
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '10.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '9.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 7
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '7.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 6
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '6.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 4
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '4.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '1.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = '-9.0';


----
-- SUB1_D,SUB2_D,SUB3_D,FREQ1_D,FREQ2_D,FREQ3_D,FREQ_ATND_SELF_HELP_D,SERVSETD

select SUB3_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by SUB3_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 19
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '19.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 18
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '18.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 17
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '17.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 16
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '16.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 15
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '15.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 14
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '14.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 13
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '13.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 12
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '12.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 11
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '11.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 10
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '10.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '9.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 8
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '8.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 7
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '7.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 6
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '6.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 4
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '4.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '1.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = '-9.0';

----
-- SUB1_D,SUB2_D,SUB3_D,FREQ1_D,FREQ2_D,FREQ3_D,FREQ_ATND_SELF_HELP_D,SERVSETD

select FREQ1_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by FREQ1_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = '1.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = '-9.0';

----
-- SUB1_D,SUB2_D,SUB3_D,FREQ1_D,FREQ2_D,FREQ3_D,FREQ_ATND_SELF_HELP_D,SERVSETD

select FREQ2_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by FREQ2_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = '1.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = '-9.0';

----
-- SUB1_D,SUB2_D,SUB3_D,FREQ1_D,FREQ2_D,FREQ3_D,FREQ_ATND_SELF_HELP_D,SERVSETD

select FREQ3_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by FREQ3_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = '1.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = '-9.0';

----

select FREQ_ATND_SELF_HELP_D
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by FREQ_ATND_SELF_HELP_D;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = 4
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = '4.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = '1.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = '-9.0';

----
-- SERVSETD

select SERVSETD
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by SERVSETD;


UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = 8
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = '8.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = 7
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = '7.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = 6
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = '6.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = 4
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = '4.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD = '-9.0';


-- ALCFLG,COKEFLG,MARFLG,HERFLG,METHFLG,OPSYNFLG,PCPFLG,HALLFLG,MTHAMFLG,AMPHFLG,STIMFLG,BENZFLG,TRNQFLG,BARBFLG,SEDHPFLG,INHFLG,OTCFLG,OTHERFLG,DIVISION,REGION,IDU,ALCDRUG,CBSA,PMSA,SERVSETD,NUMSUBS
select FREQ_ATND_SELF_HELP
from   dbo.TEDS_D_combined_data_Hawaii_2015_2021
group by FREQ_ATND_SELF_HELP;

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = 5
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = '5.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = 4
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = '4.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = 3
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = '3.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = 2
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = '2.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = 1
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = '1.0';

UPDATE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021
SET
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = -9
WHERE
    dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = '-9.0';

select
  dbo.TEDS_D_combined_data_Hawaii_2015_2021.DISYR as YearOfDischarge, 
  dbo.TEDS_D_combined_data_Hawaii_2015_2021.CASEID as Caseid,
  dbo.TEDS_D_combined_data_Hawaii_2015_2021.CBSA2010 as Cbsa2010,
  --dbo.TEDS_D_combined_data_Hawaii_2015_2021.CBSA2020 as Cbsa2020,
  dbo.TEDS_D_combined_data_Hawaii_2015_2021.CBSA as Cbsa,
  dbo.TEDS_D_combined_data_Hawaii_2015_2021.PMSA as Pmsa,
  dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVSETD as SERVSETD,
  dbo.TEDS_D_combined_data_Hawaii_2015_2021.NUMSUBS as NUMSUBS,
  dbo.TEDS_XWALK_STFIPS.value as CensusStateFipsCode,
  dbo.TEDS_XWALK_EDUC.value as Education,
  dbo.TEDS_XWALK_MARSTAT.value as MaritalStatus,
  dbo.TEDS_XWALK_SERVICES.value as TypeOfTreatmentServiceSetting,
  dbo.TEDS_XWALK_DETCRIM.value as DetailedCriminalJusticeReferral,
  dbo.TEDS_XWALK_NOPRIOR.value as PreviousSubstanceUseTreatmentEpisodes,
  dbo.TEDS_XWALK_PSOURCE.value as ReferralSource, 
  dbo.TEDS_XWALK_ARRESTS.value as ArrestsInPast30Days,
  dbo.TEDS_XWALK_EMPLOY.value as EmploymentStatus,
  dbo.TEDS_XWALK_METHUSE.value as MedicationAssistedOpioidTherapy,
  dbo.TEDS_XWALK_PSYPROB.value as CoOccurringMentalAndSubstanceUseDisorders,
  dbo.TEDS_XWALK_PREG.value as PregnantAtAdmission,
  dbo.TEDS_XWALK_GENDER.value as Gender,
  dbo.TEDS_XWALK_VET.value as VeteranStatus,
  dbo.TEDS_XWALK_LIVARAG.value as LivingArrangements,
  dbo.TEDS_XWALK_DAYWAIT.value as DaysWaitingToEnterSubstanceUseTreatment,
  dbo.TEDS_XWALK_DSMCRIT.value as DsmDiagnosisSuds4OrSuds19,
  dbo.TEDS_XWALK_AGE.value as AgeAtAdmission,
  dbo.TEDS_XWALK_RACE.value as Race,
  dbo.TEDS_XWALK_ETHNIC.value as Ethnicity,
  dbo.TEDS_XWALK_DETNLF.value as DetailedNotInLaborForce,
  dbo.TEDS_XWALK_PRIMINC.value as SourceOfIncomeSupport,
  dbo.TEDS_XWALK_SUB1.value as SubstanceUsePrimary,
  dbo.TEDS_XWALK_SUB2.value as SubstanceUseSecondary,
  dbo.TEDS_XWALK_SUB3.value as SubstanceUseTertiary,
  dbo.TEDS_XWALK_ROUTE1.value as RouteOfAdministrationPrimary,
  dbo.TEDS_XWALK_ROUTE2.value as RouteOfAdministrationSecondary,
  dbo.TEDS_XWALK_ROUTE3.value as RouteOfAdministrationTertiary,
  dbo.TEDS_XWALK_FREQ1.value as FrequencyOfUsePrimary,
  dbo.TEDS_XWALK_FREQ2.value as FrequencyOfUseSecondary,
  dbo.TEDS_XWALK_FREQ3.value as FrequencyOfUseTertiary,
  dbo.TEDS_XWALK_FRSTUSE1.value as AgeAtFirstUsePrimary,
  dbo.TEDS_XWALK_FRSTUSE2.value as AgeAtFirstUseSecondary,
  dbo.TEDS_XWALK_FRSTUSE3.value as AgeAtFirstUseTertiary,
  dbo.TEDS_XWALK_HLTHINS.value as HealthInsurance,
  dbo.TEDS_XWALK_PRIMPAY.value as PaymentSourcePrimaryExpectedOrActual,
  dbo.TEDS_XWALK_FREQ_ATND_SELF_HELP.value as AttendanceAtSubstanceUseSelfHelpGroupsInPast30,
  dbo.TEDS_XWALK_ALCFLG.value as AlcoholReportedAtAdmission,
  dbo.TEDS_XWALK_COKEFLG.value as CocaineCrackReportedAtAdmission,
  dbo.TEDS_XWALK_MARFLG.value as MarijuanaHashishReportedAtAdmission,
  dbo.TEDS_XWALK_HERFLG.value as HeroinReportedAtAdmission,
  dbo.TEDS_XWALK_METHFLG.value as NonRxMethadoneReportedAtAdmission,
  dbo.TEDS_XWALK_OPSYNFLG.value as OtherOpiatesSyntheticsReportedAtAdmission,
  dbo.TEDS_XWALK_PCPFLG.value as PcpReportedAtAdmission,
  dbo.TEDS_XWALK_HALLFLG.value as HallucinogensReportedAtAdmission,
  dbo.TEDS_XWALK_MTHAMFLG.value as MethamphetamineSpeedReportedAtAdmission,
  dbo.TEDS_XWALK_AMPHFLG.value as OtherAmphetaminesReportedAtAdmission,
  dbo.TEDS_XWALK_STIMFLG.value as OtherStimulantsReportedAtAdmission,
  dbo.TEDS_XWALK_BENZFLG.value as BenzodiazepinesReportedAtAdmission,
  dbo.TEDS_XWALK_TRNQFLG.value as OtherTranquilizersReportedAtAdmission,
  dbo.TEDS_XWALK_BARBFLG.value as BarbituratesReportedAtAdmission,
  dbo.TEDS_XWALK_SEDHPFLG.value as OtherSedativesHypnoticsReportedAtAdmission,
  dbo.TEDS_XWALK_INHFLG.value as InhalantsReportedAtAdmission,
  dbo.TEDS_XWALK_OTCFLG.value as OverTheCounterMedicationReportedAtAdmission,
  dbo.TEDS_XWALK_OTHERFLG.value as OtherDrugReportedAtAdmission,
  dbo.TEDS_XWALK_DIVISION.value as CensusDivision,
  dbo.TEDS_XWALK_REGION.value as CensusRegion,
  dbo.TEDS_XWALK_IDU.value as CurrentIvDrugUseReportedAtAdmission,
  dbo.TEDS_XWALK_ALCDRUG.value as SubstanceUseType,
  dbo.TEDS_XWALK_LOS.value as LengthOfStayInTreatment, 
  dbo.TEDS_XWALK_SERVICES_D.value as ServiceTypeAtDischarge, 
  dbo.TEDS_XWALK_REASON.value as DischargeReason, 
  dbo.TEDS_XWALK_EMPLOY_D.value as EmploymentStatusAtDischarge, 
  dbo.TEDS_XWALK_LIVARAG_D.value as LivingArrangementsAtDischarge, 
  dbo.TEDS_XWALK_ARRESTS_D.value as ArrestsBeforeDischarge, 
  dbo.TEDS_XWALK_DETNLF_D.value as DetailedNotInLaborForceAtDischarge, 
  dbo.TEDS_XWALK_SUB1_D.value as SubstanceUseAtDischargePrimary, 
  dbo.TEDS_XWALK_SUB2_D.value as SubstanceUseAtDischargeSecondary, 
  dbo.TEDS_XWALK_SUB3_D.value as SubstanceUseAtDischargeTertiary, 
  dbo.TEDS_XWALK_FREQ1_D.value as FrequencyOfUseAtDischargePrimary, 
  dbo.TEDS_XWALK_FREQ2_D.value as FrequencyOfUseAtDischargeSecondary, 
  dbo.TEDS_XWALK_FREQ3_D.value as FrequencyOfUseAtDischargeTertiary, 
  dbo.TEDS_XWALK_FREQ_ATND_SELF_HELP_D.value as AttendSubUseSelfHelpGroupsInPast30B4Discharge
into dbo.TEDS_D
from 
  dbo.TEDS_D_combined_data_Hawaii_2015_2021
  LEFT JOIN dbo.TEDS_XWALK_STFIPS ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.STFIPS = dbo.TEDS_XWALK_STFIPS.id
  LEFT JOIN dbo.TEDS_XWALK_EDUC ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.EDUC = dbo.TEDS_XWALK_EDUC.id
  LEFT JOIN dbo.TEDS_XWALK_MARSTAT ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.MARSTAT = dbo.TEDS_XWALK_MARSTAT.id
  LEFT JOIN dbo.TEDS_XWALK_SERVICES ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES = dbo.TEDS_XWALK_SERVICES.id
  LEFT JOIN dbo.TEDS_XWALK_DETCRIM ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETCRIM = dbo.TEDS_XWALK_DETCRIM.id
  LEFT JOIN dbo.TEDS_XWALK_NOPRIOR ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.NOPRIOR = dbo.TEDS_XWALK_NOPRIOR.id
  LEFT JOIN dbo.TEDS_XWALK_PSOURCE ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.PSOURCE = dbo.TEDS_XWALK_PSOURCE.id
  LEFT JOIN dbo.TEDS_XWALK_ARRESTS ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS = dbo.TEDS_XWALK_ARRESTS.id 
  LEFT JOIN dbo.TEDS_XWALK_EMPLOY ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY = dbo.TEDS_XWALK_EMPLOY.id
  LEFT JOIN dbo.TEDS_XWALK_METHUSE ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.METHUSE = dbo.TEDS_XWALK_METHUSE.id 
  LEFT JOIN dbo.TEDS_XWALK_PSYPROB ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.PSYPROB = dbo.TEDS_XWALK_PSYPROB.id
  LEFT JOIN dbo.TEDS_XWALK_PREG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.PREG = dbo.TEDS_XWALK_PREG.id
  LEFT JOIN dbo.TEDS_XWALK_GENDER ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.GENDER = dbo.TEDS_XWALK_GENDER.id
  LEFT JOIN dbo.TEDS_XWALK_VET ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.VET = dbo.TEDS_XWALK_VET.id
  LEFT JOIN dbo.TEDS_XWALK_LIVARAG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG = dbo.TEDS_XWALK_LIVARAG.id
  LEFT JOIN dbo.TEDS_XWALK_DAYWAIT ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.DAYWAIT = dbo.TEDS_XWALK_DAYWAIT.id
  LEFT JOIN dbo.TEDS_XWALK_DSMCRIT ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.DSMCRIT = dbo.TEDS_XWALK_DSMCRIT.id
  LEFT JOIN dbo.TEDS_XWALK_AGE ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.AGE = dbo.TEDS_XWALK_AGE.id
  LEFT JOIN dbo.TEDS_XWALK_RACE ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.RACE = dbo.TEDS_XWALK_RACE.id
  LEFT JOIN dbo.TEDS_XWALK_ETHNIC ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.ETHNIC = dbo.TEDS_XWALK_ETHNIC.id
  LEFT JOIN dbo.TEDS_XWALK_DETNLF ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF = dbo.TEDS_XWALK_DETNLF.id
  LEFT JOIN dbo.TEDS_XWALK_PRIMINC ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.PRIMINC = dbo.TEDS_XWALK_PRIMINC.id
  LEFT JOIN dbo.TEDS_XWALK_SUB1 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1 = dbo.TEDS_XWALK_SUB1.id
  LEFT JOIN dbo.TEDS_XWALK_SUB2 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2 = dbo.TEDS_XWALK_SUB2.id
  LEFT JOIN dbo.TEDS_XWALK_SUB3 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3 = dbo.TEDS_XWALK_SUB3.id
  LEFT JOIN dbo.TEDS_XWALK_ROUTE1 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.ROUTE1 = dbo.TEDS_XWALK_ROUTE1.id
  LEFT JOIN dbo.TEDS_XWALK_ROUTE2 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.ROUTE2 = dbo.TEDS_XWALK_ROUTE2.id
  LEFT JOIN dbo.TEDS_XWALK_ROUTE3 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.ROUTE3 = dbo.TEDS_XWALK_ROUTE3.id
  LEFT JOIN dbo.TEDS_XWALK_FREQ1 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1 = dbo.TEDS_XWALK_FREQ1.id
  LEFT JOIN dbo.TEDS_XWALK_FREQ2 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2 = dbo.TEDS_XWALK_FREQ2.id
  LEFT JOIN dbo.TEDS_XWALK_FREQ3 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3 = dbo.TEDS_XWALK_FREQ3.id
  LEFT JOIN dbo.TEDS_XWALK_FRSTUSE1 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.FRSTUSE1 = dbo.TEDS_XWALK_FRSTUSE1.id
  LEFT JOIN dbo.TEDS_XWALK_FRSTUSE2 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.FRSTUSE2 = dbo.TEDS_XWALK_FRSTUSE2.id
  LEFT JOIN dbo.TEDS_XWALK_FRSTUSE3 ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.FRSTUSE3 = dbo.TEDS_XWALK_FRSTUSE3.id
  LEFT JOIN dbo.TEDS_XWALK_HLTHINS ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.HLTHINS = dbo.TEDS_XWALK_HLTHINS.id
  LEFT JOIN dbo.TEDS_XWALK_PRIMPAY ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.PRIMPAY = dbo.TEDS_XWALK_PRIMPAY.id
  LEFT JOIN dbo.TEDS_XWALK_FREQ_ATND_SELF_HELP ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP = dbo.TEDS_XWALK_FREQ_ATND_SELF_HELP.id
  LEFT JOIN dbo.TEDS_XWALK_ALCFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.ALCFLG = dbo.TEDS_XWALK_ALCFLG.id
  LEFT JOIN dbo.TEDS_XWALK_COKEFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.COKEFLG = dbo.TEDS_XWALK_COKEFLG.id
  LEFT JOIN dbo.TEDS_XWALK_MARFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.MARFLG = dbo.TEDS_XWALK_MARFLG.id
  LEFT JOIN dbo.TEDS_XWALK_HERFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.HERFLG = dbo.TEDS_XWALK_HERFLG.id
  LEFT JOIN dbo.TEDS_XWALK_METHFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.METHFLG = dbo.TEDS_XWALK_METHFLG.id
  LEFT JOIN dbo.TEDS_XWALK_OPSYNFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.OPSYNFLG = dbo.TEDS_XWALK_OPSYNFLG.id
  LEFT JOIN dbo.TEDS_XWALK_PCPFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.PCPFLG = dbo.TEDS_XWALK_PCPFLG.id
  LEFT JOIN dbo.TEDS_XWALK_HALLFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.HALLFLG = dbo.TEDS_XWALK_HALLFLG.id
  LEFT JOIN dbo.TEDS_XWALK_MTHAMFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.MTHAMFLG = dbo.TEDS_XWALK_MTHAMFLG.id
  LEFT JOIN dbo.TEDS_XWALK_AMPHFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.AMPHFLG = dbo.TEDS_XWALK_AMPHFLG.id
  LEFT JOIN dbo.TEDS_XWALK_STIMFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.STIMFLG = dbo.TEDS_XWALK_STIMFLG.id
  LEFT JOIN dbo.TEDS_XWALK_BENZFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.BENZFLG = dbo.TEDS_XWALK_BENZFLG.id
  LEFT JOIN dbo.TEDS_XWALK_TRNQFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.TRNQFLG = dbo.TEDS_XWALK_TRNQFLG.id
  LEFT JOIN dbo.TEDS_XWALK_BARBFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.BARBFLG = dbo.TEDS_XWALK_BARBFLG.id
  LEFT JOIN dbo.TEDS_XWALK_SEDHPFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.SEDHPFLG = dbo.TEDS_XWALK_SEDHPFLG.id
  LEFT JOIN dbo.TEDS_XWALK_INHFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.INHFLG = dbo.TEDS_XWALK_INHFLG.id
  LEFT JOIN dbo.TEDS_XWALK_OTCFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.OTCFLG = dbo.TEDS_XWALK_OTCFLG.id
  LEFT JOIN dbo.TEDS_XWALK_OTHERFLG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.OTHERFLG = dbo.TEDS_XWALK_OTHERFLG.id
  LEFT JOIN dbo.TEDS_XWALK_DIVISION ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.DIVISION = dbo.TEDS_XWALK_DIVISION.id
  LEFT JOIN dbo.TEDS_XWALK_REGION ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.REGION = dbo.TEDS_XWALK_REGION.id
  LEFT JOIN dbo.TEDS_XWALK_IDU ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.IDU = dbo.TEDS_XWALK_IDU.id
  LEFT JOIN dbo.TEDS_XWALK_ALCDRUG ON  dbo.TEDS_D_combined_data_Hawaii_2015_2021.ALCDRUG = dbo.TEDS_XWALK_ALCDRUG.id
  LEFT JOIN dbo.TEDS_XWALK_LOS ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.LOS = dbo.TEDS_XWALK_LOS.id
  LEFT JOIN dbo.TEDS_XWALK_SERVICES_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.SERVICES_D = dbo.TEDS_XWALK_SERVICES_D.id
  LEFT JOIN dbo.TEDS_XWALK_REASON ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.REASON = dbo.TEDS_XWALK_REASON.id
  LEFT JOIN dbo.TEDS_XWALK_EMPLOY_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.EMPLOY_D = dbo.TEDS_XWALK_EMPLOY_D.id
  LEFT JOIN dbo.TEDS_XWALK_LIVARAG_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.LIVARAG_D = dbo.TEDS_XWALK_LIVARAG_D.id
  LEFT JOIN dbo.TEDS_XWALK_ARRESTS_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.ARRESTS_D = dbo.TEDS_XWALK_ARRESTS_D.id
  LEFT JOIN dbo.TEDS_XWALK_DETNLF_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.DETNLF_D = dbo.TEDS_XWALK_DETNLF_D.id
  LEFT JOIN dbo.TEDS_XWALK_SUB1_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB1_D = dbo.TEDS_XWALK_SUB1_D.id
  LEFT JOIN dbo.TEDS_XWALK_SUB2_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB2_D = dbo.TEDS_XWALK_SUB2_D.id
  LEFT JOIN dbo.TEDS_XWALK_SUB3_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.SUB3_D = dbo.TEDS_XWALK_SUB3_D.id
  LEFT JOIN dbo.TEDS_XWALK_FREQ1_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ1_D = dbo.TEDS_XWALK_FREQ1_D.id
  LEFT JOIN dbo.TEDS_XWALK_FREQ2_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ2_D = dbo.TEDS_XWALK_FREQ2_D.id
  LEFT JOIN dbo.TEDS_XWALK_FREQ3_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ3_D = dbo.TEDS_XWALK_FREQ3_D.id
  LEFT JOIN dbo.TEDS_XWALK_FREQ_ATND_SELF_HELP_D ON dbo.TEDS_D_combined_data_Hawaii_2015_2021.FREQ_ATND_SELF_HELP_D = dbo.TEDS_XWALK_FREQ_ATND_SELF_HELP_D.id;

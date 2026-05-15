select count(*) from dbo.Naloxone;
select * from dbo.Naloxone where zipcode = '96720';
--update dbo.Naloxone set zipcode = '96720' where zipcode = '95720';
select * from dbo.Naloxone where city = 'Honoulu';
-- update dbo.Naloxone set city = 'Honolulu' where city = 'Honoulu';
-- update dbo.Naloxone set city = 'Honolulu' where city = 'Hono;ulu';
-- update dbo.Naloxone set city = 'Kailua-Kona' where city = 'Kailua Kona';
-- update dbo.Naloxone set city = 'Kailua-Kona' where city = 'Kailu-Kona';
-- update dbo.Naloxone set city = 'Wailuku' where city = 'Waikuku';
-- update dbo.Naloxone set county = 'Maui' where city = 'Kahului' and county = 'Oahu';
-- update dbo.Naloxone set city = 'Kailua', county = 'Oahu' where city = 'Kkailua' and county = 'Maui' and zipcode = '96734';
-- update dbo.Naloxone set org_type = 'Government Agency (City/County)' where org_type = 'Government Agency';
-- update dbo.Naloxone set org_type = 'Government Agency (City/County)' where org_type = 'Government Agency (City';
-- update dbo.Naloxone set org_type = 'Law Enforcement/EMS' where org_type = 'Law Enforcement';
-- update dbo.Naloxone set org_type = 'Law Enforcement/EMS' where org_type = 'EMS';
select * from dbo.Naloxone where org_type = 'Government Agency';
select distinct org_type from dbo.Naloxone;


ALTER TABLE dbo.Naloxone ALTER COLUMN funds_type VARCHAR(30);  
select distinct funds_type from dbo.Naloxone;
select count(*) from dbo.Naloxone where funds_type = 'OSP';
update dbo.Naloxone set funds_type = 'Opioid Settlement Program' where funds_type = 'OSP';
update dbo.Naloxone set funds_type = 'State Opioid Response' where funds_type = 'SOR';

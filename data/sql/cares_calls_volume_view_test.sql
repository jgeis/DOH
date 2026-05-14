/****** Object:  View [dbo].[cares_calls_volume_view]    Script Date: 4/27/2026 3:56:54 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO



ALTER VIEW [dbo].[cares_calls_volume_view] AS

SELECT 
    Day as Date, 
    Count_of_Users as total_calls, 
    Origin_of_Call as phone 
FROM [dbo].[cares_calls_clean_text_chat]
UNION ALL
SELECT 
    Date, 
    total_calls, 
    phone
FROM [dbo].[cares_calls_clean];
GO



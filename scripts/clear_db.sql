USE car_dealer;
GO

DECLARE @sql nvarchar(max) = N'';

SELECT @sql += N'DROP VIEW [' + s.name + N'].[' + v.name + N'];' + CHAR(10)
FROM sys.views v
JOIN sys.schemas s ON v.schema_id = s.schema_id
WHERE s.name IN ('dbo', 'stg', 'int', 'marts')
  AND (s.name <> 'dbo' OR v.name IN ('v_sessions', 'v_clients', 'v_medium'));

SELECT @sql += N'DROP TABLE [' + s.name + N'].[' + t.name + N'];' + CHAR(10)
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name IN ('stg', 'int', 'marts')
   OR (s.name = 'dbo' AND t.name IN (
        'ga_sessions',
        'mediums',
        'crm_events',
        'clients',
        'sales',
        'models',
        'brands',
        'classes',
        'currencies',
        'currency_rates'
   ));

EXEC sp_executesql @sql;
GO

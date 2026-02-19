CREATE DATABASE Car_Dealer_GA_CRM

-- Создаем PK
ALTER TABLE Client ALTER COLUMN ClientID nvarchar(255) NOT NULL
ALTER TABLE Client ADD CONSTRAINT PK_Client PRIMARY KEY(Client_ID)

DELETE FROM Model
WHERE Model IS NULL

ALTER TABLE Model ALTER COLUMN Model nvarchar(255) NOT NULL
ALTER TABLE Model ADD CONSTRAINT PK_Model PRIMARY KEY(Model)

ALTER TABLE Session ALTER COLUMN SessionID float NOT NULL
ALTER TABLE Session ADD CONSTRAINT PK_Session PRIMARY KEY(SessionID)

-- Создаем FK

ALTER TABLE Session ADD CONSTRAINT FK_Session_ClientID
FOREIGN KEY(ClientID) REFERENCES Client(ClientID)

ALTER TABLE Session ADD CONSTRAINT FK_Session_Model
FOREIGN KEY(Model) REFERENCES Model(Model)

-- Создаем таблицы Medium и связей с ней

CREATE TABLE Medium(
	Medium_Type nvarchar(255) NOT NULL,
	Medium_Sort int
)

INSERT INTO Medium VALUES
(N'referral',1),
(N'organic',2),
(N'(none)',3),
(N'cpc',4),
(N'sem_cpc',5),
(N'cpm',6),
(N'(not set)',7)

ALTER TABLE Medium ADD CONSTRAINT PK_Medium PRIMARY KEY(Medium_Type)

ALTER TABLE Session ADD CONSTRAINT FK_Sessions_Medium
FOREIGN KEY(Medium) REFERENCES Medium(Medium)

-- Создаем таблицу CurrencyRates и связи с ней
CREATE TABLE CurrencyRates (
    RateDate DATE,        -- Дата курса
    CurrencyCode NVARCHAR(3), -- Код (USD, EUR)
    Nominal INT,          -- Номинал (например, 1 или 100)
    RateValue DECIMAL(18, 4), -- Сам курс
    UpdateTimestamp DATETIME DEFAULT GETDATE() -- Когда данные были обновлены
)

-- Добавляем рубль, чтобы перемножать значения в рублях на 1
UPDATE m
SET CurrencyCode = 'RUB'
FROM Model m
WHERE CurrencyCode = 'Рубль'

ALTER TABLE CurrencyRates ALTER COLUMN RateDate DATE NOT NULL
ALTER TABLE CurrencyRates ALTER COLUMN CurrencyCode NVARCHAR(3) NOT NULL

ALTER TABLE CurrencyRates
ADD CONSTRAINT PK_CurrencyRates PRIMARY KEY (RateDate, CurrencyCode)


-- Создаем представления

CREATE VIEW v_sessions_final AS
SELECT 
    s.*,
    m.Brand,
    m.Margin AS ModelMarginPercent,
    m.Price AS Price_OriginalCurrency,
    m.CurrencyCode,
    cr.RateValue AS ExchangeRate,
    -- Считаем стоимость в рублях
    -- Если валюта 'RUB', курс считаем как 1
    CASE 
        WHEN m.CurrencyCode = 'RUB' THEN m.Price
        ELSE m.Price * ISNULL(cr.RateValue, 1)
    END AS PriceRub,
    -- Считаем валовую прибыль
    -- Считаем как: Цена в рублях * Процент маржинальности
    CASE 
        WHEN m.CurrencyCode = 'RUB' THEN m.Price * m.Margin
        ELSE (m.Price * ISNULL(cr.RateValue, 1)) * m.Margin
    END AS GrossProfitRub
FROM Session s
LEFT JOIN Model m ON s.Model = m.Model 
LEFT JOIN CurrencyRates cr ON s.Date = cr.RateDate 
                           AND m.CurrencyCode = cr.CurrencyCode;

-- Создаем столбец расходов на рекламу за сессию
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Session') AND name = 'AdCost')
BEGIN
    ALTER TABLE Session ADD AdCost DECIMAL(18, 2) DEFAULT 0;
END
GO

-- Заполняем столбец AdCost согласно типу рекламы

UPDATE s
SET s.AdCost = CASE 
    -- 1. ЧИСТО БЕСПЛАТНЫЕ (Поиск и прямые заходы)
    WHEN s.Medium IN ('organic', '(none)', 'not set') THEN 0
    
    -- 2. ПАРТНЕРСКИЙ ТРАФИК (Auto.ru, Avito и т.д.)
    -- Даже если это Referral, за него платят. Назначим в среднем 300-700 руб за сессию.
    WHEN s.Medium = 'referral' THEN (ABS(CHECKSUM(NEWID()) % 400) + 300)

    -- 3. КОНТЕКСТНАЯ РЕКЛАМА (Очень дорогая в авто)
    WHEN s.Medium IN ('cpc', 'sem_cpc') THEN 
        (CASE 
            WHEN s.Sale = 1 THEN (ABS(CHECKSUM(NEWID()) % 30000) + 70000) -- Продажа за 70-100к
            ELSE (ABS(CHECKSUM(NEWID()) % 2000) + 1500) -- Клик за 1.5-3.5к
        END)

    -- 4. МЕДИЙКА И СОЦСЕТИ
    WHEN s.Medium IN ('cpm', 'social') THEN (ABS(CHECKSUM(NEWID()) % 1000) + 500)

    ELSE 0 
END
FROM Session s
LEFT JOIN Model m ON s.Model = m.Model;


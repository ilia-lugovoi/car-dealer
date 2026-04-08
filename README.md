# Сквозная аналитика автодилера

## Цель проекта
1. Объединение данных Google Analytics с внутренними данными о продажах и справочником, а также настройка выгрузки курсов валют
2. Создание дашборда для оценки ROI рекламных каналов и выявления убыточных кампаний в Power BI
3. Создание дашборда для анализа выручки и просмотров сайта автодирела в Superset

## Основные используемые технологии
Power BI (Power Query, DAX, Power View), Superset, SQL Server, Views, Excel, Python (requests, pyodbc, pandas, time), Парсинг

## Структура базы данных
**Основные таблицы:**
* Client - таблица с данными о клиентах
* Session - таблица с данными по сессиям с Google Analytics и воронкой их реализации

**Справочники:**
* Model - справочник моделей авто 
* Medium - справочник типов рекламы
* CurrencyRates - справочник курсов валют по дням

**Процесс заполнения CurrencyRates полностью автоматизирован с помощью скриптов Python:**
  1. Скрипт на парсинг курсов валют с сайта ЦБ РФ за выбранные даты
  2. Скрипт на ежедневный парсинг текущих курсов валют с сайта ЦБ РФ

**Представление v_sessions_final** - денормализует данные по моделям авто и курсам валют, а также расчитывает метрики

#### Диаграмма базы данных Car_Dealer_GA_CRM
<img width="932" height="698" alt="db_diagram" src="carDealer_screens/db_diagram.png" />

## Структура Power BI
### **Модель данных:**
  - Две основные таблицы и справочник Medium
  - Таблица, созданая в Power Query PBI, для агрегации по неделям Calendar
  - Набор мер

<img width="1088" height="684" alt="модель_данныхPBI" src="carDealer_screens/PBI_charts/модель_данныхPBI.png" />

### **Фильтры:**
  - по дате
  - по марке и модели
  - по региону и городу
  - по типу трафика, кампании и ключевым словам
  - по устройству, браузеру и сайту

<img width="1590" height="113" alt="filters" src="carDealer_screens/PBI_charts/filters.png" />

### **Визуализации:**
1. "Реализация конверсий по неделям" - отражает изменение кол-ва конверсий и их реализацию в течении времени, 'воронка продаж в линейном графике по неделям'.
<img width="680" height="333" alt="chart1" src="carDealer_screens/PBI_charts/chart1.png" />

2. "Трафик конверсий по неделям" - отражает источники трафика и их эффективность в течении времени.
<img width="680" height="411" alt="chart2" src="carDealer_screens/PBI_charts/chart2.png" />

3. "Марка: доля конв. | ДРР" - отражает кол-во и эффективность конверсий и продаж марок и моделей авто.
<img width="446" height="331" alt="chart3" src="carDealer_screens/PBI_charts/chart3.png" />

4. "Устройство: доля конв. | ДРР" - отражает кол-во и эффективность конверсий и продаж по типам устройств, браузерам и сайтам.
<img width="444" height="410" alt="chart4" src="carDealer_screens/PBI_charts/chart4.png" />

5. "Город: доля конв. | ДРР" - отражает кол-во и эффективность конверсий и продаж по городам, кампаниям и ключевым словам.
<img width="422" height="316" alt="chart5" src="carDealer_screens/PBI_charts/chart5.png" />

6. "Убытки по кампаниям и keywords" - отражает убыточные кампании и ключевые слова.
<img width="446" height="412" alt="chart6" src="carDealer_screens/PBI_charts/chart6.png" />

<img width="1592" height="865" alt="full_screen" src="carDealer_screens/PBI_charts/full_screen.png" />


### **Справка по графикам и метрикам:**

<img width="736" height="403" alt="справка_PBI" src="carDealer_screens/PBI_charts/справка_PBI.png" />

## Структура Superset
### **Datasets:**
**v_sessions_final** - единственое, что отличается от представления с БД - это добавление метрик

<img width="994" height="670" alt="df_view" src="carDealer_screens/superset_charts/df_view.png" />

**client_chart** - соединенные и агрегированные v_sessions_final с Client

<img width="951" height="488" alt="df_client_chart" src="carDealer_screens/superset_charts/df_client_chart.png" />

<img width="1664" height="872" alt="df_list" src="carDealer_screens/superset_charts/df_list.png" />

### **Фильтры и визуализации:**

**Фильтры по всем основным атрибутам**

<img width="281" height="470" alt="filters" src="carDealer_screens/superset_charts/filters.png" />

* **Топ-15 городов по валовой прибыли**
<img width="656" height="589" alt="chart1" src="carDealer_screens/superset_charts/chart1.png" />

* **Валовая прибыль по маркам и моделям авто**
<img width="919" height="585" alt="chart2" src="carDealer_screens/superset_charts/chart2.png" />

* **Динамика валовой прибыли и DRR по неделям**
<img width="785" height="456" alt="chart3" src="carDealer_screens/superset_charts/chart3.png" />

* **Корреляция продаж к просмотренным страницам**
<img width="783" height="457" alt="chart4" src="carDealer_screens/superset_charts/chart4.png" />

![car-dealer-2026-04-07T19-33-13 999Z](carDealer_screens/superset_charts/car-dealer-2026-04-07T19-33-13.999Z.jpg)

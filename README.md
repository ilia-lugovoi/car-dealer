# Сквозная аналитика автодилера

## Цель проекта
1. Объединение данных Google Analytics с внутренними данными о продажах и справочником, а также настройка выгрузки курсов валют
2. Создание дашборда для оценки ROI рекламных каналов и выявления убыточных кампаний

## Основные используемые технологии:
Power BI (Power Query, DAX, Power View), Superset, SQL Server, Views, Excel, Python (requests, pyodbc, pandas, time), Парсинг

## Структура базы данных:
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
<img width="932" height="698" alt="db_diagram" src="https://github.com/user-attachments/assets/e516b37d-0477-481b-a543-ad231f6f96be" />

## Структура Power BI
* **Модель данных:**
  - Две основные таблицы и справочник Medium
  - Таблица, созданая в Power Query PBI, для агрегации по неделям Calendar
  - Набор мер
<img width="1088" height="684" alt="модель_данныхPBI" src="https://github.com/user-attachments/assets/9a1532e5-01de-414a-8ecf-7988d7cbccab" />

* **Фильтры:**
  - по дате
  - по марке и модели
  - по региону и городу
  - по типу трафика, кампании и ключевым словам
  - по устройству, браузеру и сайту
<img width="1590" height="113" alt="filters" src="https://github.com/user-attachments/assets/c26a3818-a114-4bc8-a557-9ea56e879c1d" />

* **Визуализации:**
1. "Реализация конверсий по неделям" - отражает изменение кол-ва конверсий и их реализацию в течении времени, 'воронка продаж в линейном графике по неделям'.
   <img width="680" height="333" alt="chart1" src="https://github.com/user-attachments/assets/acf98179-6128-4551-8eb3-0510394ea528" />

3. "Трафик конверсий по неделям" - отражает источники трафика и их эффективность в течении времени.
   <img width="680" height="411" alt="chart2" src="https://github.com/user-attachments/assets/f69f0663-04fa-4f7a-aa11-aba9004e7a1f" />

5. "Марка: доля конв. | ДРР" - отражает кол-во и эффективность конверсий и продаж марок и моделей авто.
   <img width="446" height="331" alt="chart3" src="https://github.com/user-attachments/assets/608bfca4-97a9-4e32-bf8f-4e0aad8732de" />

7. "Устройство: доля конв. | ДРР" - отражает кол-во и эффективность конверсий и продаж по типам устройств, браузерам и сайтам.
   <img width="444" height="410" alt="chart4" src="https://github.com/user-attachments/assets/f2ebce44-cf65-43fd-8678-83446c6d5083" />

9. "Город: доля конв. | ДРР" - отражает кол-во и эффективность конверсий и продаж по городам, кампаниям и ключевым словам.
    <img width="422" height="316" alt="chart5" src="https://github.com/user-attachments/assets/9e82a845-c75c-4ecc-8e38-e9b6e7b19b76" />

11. "Убытки по кампаниям и keywords" - отражает убыточные кампании и ключевые слова.
    <img width="446" height="412" alt="chart6" src="https://github.com/user-attachments/assets/276b88f7-0f3f-474a-824e-f5f03287cebb" />


* **Справка по графикам и метрикам:**
<img width="736" height="403" alt="справка_PBI" src="https://github.com/user-attachments/assets/24b0ca99-9f87-45d0-b722-70d9ced4239d" />

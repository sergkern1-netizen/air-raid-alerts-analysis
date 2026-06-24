# Air Raid Alerts MVP Design — 1 Day Challenge

**Goal:** Полный рабочий проект с анализом и моделью за 1 день (12 часов)

**Architecture:** 3-источниковая система с кросс-проверкой данных

**Tech Stack:** pandas, numpy, matplotlib, alerts-ua-py, statsmodels

---

## 🎯 Дизайн системы

### Data Flow:
```
3 ИСТОЧНИКА ДАННЫХ (параллельно)
    ├─ GitHub Vadimkin (CSV) → 30 мин
    ├─ Kaggle dimakyn (CSV) → 15 мин
    └─ Alerts-ua-py API → 90 мин (+ регистрация)
        ↓
ВАЛИДАЦИЯ И КРОСС-ПРОВЕРКА (30 мин)
    ├─ Совпадают ли данные за общий период?
    ├─ Аномалии в источниках?
    └─ Финальный датасет (объединенный)
        ↓
АНАЛИЗ (EDA) (3 часа)
    ├─ Статистика по регионам
    ├─ Суточные/недельные паттерны
    ├─ Тренды
    └─ Визуализация
        ↓
МОДЕЛЬ (ARIMA) (2 часа)
    ├─ Обучение на историческом датасете
    ├─ Прогноз на 7 дней
    └─ Валидация
        ↓
ОТЧЕТ (Jupyter Notebook) (1 час)
    └─ Выводы + графики + insights
```

---

## 📁 Структура проекта (УПРОЩЁННАЯ для 1 дня)

```
air-raid-alerts-analysis/
├── data/
│   ├── raw/
│   │   ├── github_vadimkin.csv       # Скачанный
│   │   ├── kaggle_dimakyn.csv        # Скачанный
│   │   └── alerts_api_live.csv       # Загруженный через API
│   └── processed/
│       └── validated_combined.csv    # Объединённый датасет
├── src/
│   ├── loader.py                     # Загрузка из 3 источников
│   ├── validator.py                  # Кросс-проверка
│   └── analyzer.py                   # EDA + ARIMA
├── notebooks/
│   └── 01-full-analysis.ipynb        # ГЛАВНЫЙ РЕЗУЛЬТАТ
├── requirements.txt
└── README.md
```

---

## 🔧 Компоненты (минимальные)

### 1. **Loader** (src/loader.py)
- `load_github()` — читать CSV из GitHub
- `load_kaggle()` — читать CSV из Kaggle
- `load_alerts_api()` — fetch из Alerts-ua-py API

### 2. **Validator** (src/validator.py)
- `cross_validate()` — сравнить 3 источника
- `detect_anomalies()` — найти расхождения
- `combine_sources()` — объединить надёжные данные

### 3. **Analyzer** (src/analyzer.py)
- `basic_stats()` — статистика
- `detect_patterns()` — паттерны
- `arima_forecast()` — прогноз

### 4. **Notebook** (notebooks/01-full-analysis.ipynb)
- Импорт модулей
- Загрузка + валидация
- EDA с графиками
- ARIMA модель
- Выводы

---

## ⏱️ ТОЧНЫЙ TIMELINE

| Фаза | Что | Время | Ответ |
|------|-----|-------|--------|
| 1 | Загрузка GitHub CSV | 30 мин | `pd.read_csv()` |
| 2 | Загрузка Kaggle CSV | 15 мин | `pd.read_csv()` |
| 3 | Регистрация Alerts.in.ua + токен | 15 мин | Web form |
| 4 | Загрузка Alerts-ua-py API | 60 мин | `AlertsUA()` |
| 5 | Кросс-проверка 3 источников | 30 мин | `validator.py` |
| 6 | EDA + Visualization | 3 часа | `analyzer.py` |
| 7 | ARIMA модель + прогноз | 2 часа | `statsmodels` |
| 8 | Финальный Notebook | 1 час | `.ipynb` |
| **ИТОГО** | | **~12 часов** | ✅ |

---

## 📊 Ожидаемый результат за день

✅ **Загруженные данные:** ~100,000+ записей из 3 источников  
✅ **Валидация:** Проверена консистентность между источниками  
✅ **EDA:** 5-7 графиков + insights по паттернам  
✅ **Модель:** ARIMA с прогнозом на 7 дней  
✅ **Отчет:** Jupyter notebook с выводами  
✅ **Код:** Python модули для повторного использования  

---

## 🎁 Bonus: Кросс-проверка трёх источников

```python
# Пример: совпадают ли данные?
github_daily = github_df.groupby('date').size()
kaggle_daily = kaggle_df.groupby('date').size()
alerts_daily = alerts_df.groupby('date').size()

# Сравнение за общий период
common_period = (
    github_df['date'].min().max(kaggle_df['date'].min(), alerts_df['date'].min()),
    github_df['date'].max().min(kaggle_df['date'].max(), alerts_df['date'].max())
)

# Корреляция между источниками
correlation = github_daily.corr(kaggle_daily)
print(f"GitHub ↔ Kaggle correlation: {correlation:.2%}")
```

---

## 🚀 Начало работы

1. Создать `src/loader.py`, `src/validator.py`, `src/analyzer.py`
2. Скачать GitHub + Kaggle CSV в `data/raw/`
3. Создать Alerts API токен
4. Написать загрузчик для API
5. Кросс-проверить данные
6. Написать EDA анализ
7. Построить ARIMA модель
8. Собрать всё в Notebook
9. Commit и готово! ✅

---

## ❌ ЧТО НЕ ДЕЛАЕМ (чтобы уложиться в день)

- ❌ Ensemble моделей (Prophet, LSTM)
- ❌ Интерактивные Streamlit приложения
- ❌ Web API (FastAPI)
- ❌ Docker контейнеры
- ❌ CI/CD pipelines
- ❌ Расширенная документация

Всё это потом, после MVP! 🚀

# Мастер-документ дослідження: План реалізації

> **Для агентних робітників:** ОБОВ'ЯЗКОВИЙ ПІДНАВИК: Використовуйте superpowers:subagent-driven-development (рекомендується) або superpowers:executing-plans для реалізації цього плану завдання за завданням. Кроки використовують синтаксис checkbox (`- [ ]`) для відстеження.

**Мета:** Створити комплексний дослідницький документ RESEARCH_REPORT_UK.md (32-41 сторінка) на українській мові з реальними даними з 15 CSV файлів, таблицями, графіками та висновками.

**Архітектура:** 
- Phase 1: Читання та валідація даних з CSV файлів
- Phase 2: Генерація основного markdown документа з 12 розділами
- Phase 3: Вставлення таблиць з реальними даними
- Phase 4: Генерація графіків (Plotly) та додатків
- Phase 5: Перевірка якості та commit

**Технічний стек:** Python (pandas, plotly), Markdown, Git

---

## Структура файлів

**Основні файли:**
- **Створити:** `RESEARCH_REPORT_UK.md` (корінь проекту, 32-41 сторінка)
- **Допоміжні скрипти:** `scripts/generate_research_report.py`
- **Логи:** `logs/report_generation.log`
- **Тести:** `tests/test_research_report.py`

**CSV джерела (читаємо звідси):**
```
data/processed/01_daily_aggregates.csv
data/processed/02_regional_summary.csv
data/processed/03_regional_daily.csv
data/processed/04_yearly_comparison.csv
data/processed/05_duration_statistics.csv
data/processed/07_yearly_statistics.csv
data/processed/08_monthly_pattern.csv
data/processed/09_month_year_matrix.csv
data/processed/10_quarterly_pattern.csv
data/processed/11_peak_weeks.csv
data/processed/13_regional_ranking.csv
data/processed/15_duration_by_region.csv
data/processed/16_regional_trends.csv
data/processed/18_recent_escalation.csv
data/processed/20_KEY_FINDINGS.md
```

---

## PHASE 1: Підготовка та валідація даних (2-3 години)

### Task 1: Створити генеруючий скрипт та тести

**Файли:**
- Створити: `scripts/generate_research_report.py`
- Створити: `tests/test_research_report.py`

- [ ] **Крок 1: Написати тест для читання CSV файлів**

```python
# tests/test_research_report.py
import pandas as pd
import os
from pathlib import Path

def test_csv_files_exist():
    """Перевірити, що всі необхідні CSV файли існують"""
    csv_files = [
        'data/processed/01_daily_aggregates.csv',
        'data/processed/02_regional_summary.csv',
        'data/processed/03_regional_daily.csv',
        'data/processed/04_yearly_comparison.csv',
        'data/processed/05_duration_statistics.csv',
        'data/processed/07_yearly_statistics.csv',
        'data/processed/08_monthly_pattern.csv',
        'data/processed/09_month_year_matrix.csv',
        'data/processed/10_quarterly_pattern.csv',
        'data/processed/11_peak_weeks.csv',
        'data/processed/13_regional_ranking.csv',
        'data/processed/15_duration_by_region.csv',
        'data/processed/16_regional_trends.csv',
        'data/processed/18_recent_escalation.csv',
    ]
    
    for csv_file in csv_files:
        assert os.path.exists(csv_file), f"CSV файл не знайдено: {csv_file}"
        df = pd.read_csv(csv_file)
        assert len(df) > 0, f"CSV файл пустий: {csv_file}"

def test_csv_data_quality():
    """Перевірити якість даних в CSV"""
    daily = pd.read_csv('data/processed/01_daily_aggregates.csv')
    
    # Перевірити, що є стовпці які очікуємо
    assert len(daily) >= 1500, "Мало днів для аналізу"
```

- [ ] **Крок 2: Написати базовий генеруючий скрипт**

```python
# scripts/generate_research_report.py
import pandas as pd
from pathlib import Path
from datetime import datetime

class ResearchReportGenerator:
    """Генератор дослідницького звіту на українській"""
    
    def __init__(self):
        self.data_dir = Path('data/processed')
        self.output_file = 'RESEARCH_REPORT_UK.md'
        self.data = {}
        self.report_content = []
        
    def load_data(self):
        """Завантажити всі CSV файли"""
        csv_files = {
            'daily': '01_daily_aggregates.csv',
            'regional': '02_regional_summary.csv',
            'yearly_stats': '07_yearly_statistics.csv',
        }
        
        for key, filename in csv_files.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                self.data[key] = pd.read_csv(filepath)
                print(f"✓ Завантажено {filename}")
    
    def generate_report(self):
        """Генерувати звіт"""
        self._add_header()
        self._add_resume()
        
    def _add_header(self):
        """Додати титульну сторінку"""
        header = """# Прогнозування та аналіз повітряних тривог

Період аналізу: 15 липня 2022 — 24 червня 2026
Кількість записів: 418,838
Регіони: 25 українських областей
"""
        self.report_content.append(header)
    
    def _add_resume(self):
        """Додати резюме"""
        resume = """## РЕЗЮМЕ

Дослідження аналізує 418,838 записів про повітряні тривоги в Україні.
"""
        self.report_content.append(resume)
    
    def save_report(self):
        """Зберегти звіт у файл"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.report_content))
        print(f"✓ Звіт збережено: {self.output_file}")

if __name__ == '__main__':
    generator = ResearchReportGenerator()
    generator.load_data()
    generator.generate_report()
    generator.save_report()
```

- [ ] **Крок 3-6: Запустити, перевірити та commit**

```bash
pytest tests/test_research_report.py -v
python scripts/generate_research_report.py
git add scripts/generate_research_report.py tests/test_research_report.py
git commit -m "feat: add research report generator script and tests"
```

---

## PHASE 2: Генерація основних розділів (4-5 годин)

### Task 2: Розширити скрипт для всіх 12 розділів

Розширити ResearchReportGenerator з методами для EDA, Findings, Regional, Temporal, Limitations, Models розділів.

---

## PHASE 3: Генерація графіків (2-3 години)

### Task 3: Додати Plotly графіки

Створити scripts/generate_plots.py для генерації 3+ інтерактивних графіків.

---

## PHASE 4: Валідація якості (1-2 години)

### Task 4: Тестування якості звіту

Додати 8+ тестів для валідації структури, мови, таблиць звіту.

---

## PHASE 5: Фінальна сборка (30 хв)

### Task 5: Фінальний commit та README

Оновити README та зробити фінальний commit усіх файлів.

---

## SUMMARY

| Фаза | Задача | Статус |
|------|--------|--------|
| 1 | Генератор + тести | ⏳ |
| 2 | 12 розділів | ⏳ |
| 3 | Графіки | ⏳ |
| 4 | Валідація | ⏳ |
| 5 | Фінал | ⏳ |

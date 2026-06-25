# Setup Instructions for Disk D Environment

## Overview

Проект переместил Python на диск D для решения проблемы нехватки дискового пространства.

**Текущая конфигурация:**
- Python 3.11.9: `D:\Python 3.11\`
- TensorFlow venv: `D:\tf_env\`
- Проект: `D:\Нова папка\air-raid-alerts-analysis\`

## Environment Setup

### Option 1: Using TensorFlow venv (Recommended)

Для запуска проекта с поддержкой TensorFlow и LSTM:

```powershell
# Перейти в папку проекта
cd "D:\Нова папка\air-raid-alerts-analysis"

# Активировать venv с TensorFlow
& "D:\tf_env\Scripts\Activate.ps1"

# Запустить тесты
python -m pytest tests/ -v

# Запустить Jupyter notebook
jupyter notebook notebooks/02-advanced-analytics.ipynb
```

### Option 2: Using Main Python (D:\Python 3.11)

Если TensorFlow/LSTM не требуется:

```powershell
# Перейти в папку проекта
cd "D:\Нова папка\air-raid-alerts-analysis"

# Установить зависимости
"D:\Python 3.11\python.exe" -m pip install -r requirements.txt

# Запустить тесты (без LSTM тестов)
"D:\Python 3.11\python.exe" -m pytest tests/ -v -k "not lstm"
```

## Verifying Setup

Проверить, что окружение готово:

```powershell
# Проверить Python
python --version

# Проверить TensorFlow
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__}')"

# Проверить Prophet
python -c "from prophet import Prophet; print('Prophet available')"

# Проверить все зависимости
python -m pip list
```

## Running Tests

### All Tests (with TensorFlow support)

```powershell
& "D:\tf_env\Scripts\Activate.ps1"
python -m pytest tests/ -v
```

Expected: 19/20 PASSED (Prophet test may fail if Prophet not installed)

### Specific Test Suite

```powershell
# Only LSTM tests
python -m pytest tests/test_lstm.py -v

# Only Ensemble tests
python -m pytest tests/test_ensemble.py -v

# Only ExponentialSmoothing tests
python -m pytest tests/test_exponential_smoothing.py -v
```

## Important Paths

**Do NOT hardcode these paths.** They are documented here for reference only.

- Python executable: `D:\Python 3.11\python.exe`
- Pip executable: `D:\Python 3.11\Scripts\pip.exe`
- TensorFlow venv: `D:\tf_env\Scripts\Activate.ps1`
- Project root: `D:\Нова папка\air-raid-alerts-analysis\`
- Requirements: `D:\Нова папка\air-raid-alerts-analysis\requirements.txt`

Always use relative paths or environment variables instead.

## Troubleshooting

### "python command not found"

Use full path to Python executable:
```powershell
"D:\Python 3.11\python.exe" --version
```

Or activate venv:
```powershell
& "D:\tf_env\Scripts\Activate.ps1"
python --version
```

### "No module named tensorflow"

Ensure TensorFlow venv is activated:
```powershell
& "D:\tf_env\Scripts\Activate.ps1"
python -c "import tensorflow as tf; print(tf.__version__)"
```

### Tests fail with "No space left on device"

Disk C may be full. Use Disk D for all operations.

## Future Considerations

If upgrading packages, ensure Disk D has sufficient space (120+ GB available).

For new team members: use TensorFlow venv to avoid environment conflicts.

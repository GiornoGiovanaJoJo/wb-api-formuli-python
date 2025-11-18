# 🚀 Multi-Report Loader - Массовая загрузка отчётов WB

## Описание

`MultiReportLoader` — класс для **параллельной загрузки множества отчётов WB API** одновременно.

### ✅ Преимущества:

- **Параллельность** - все отчёты загружаются одновременно (asyncio + aiohttp)
- **Единый файл** - результаты объединяются в один JSON
- **Универсальность** - поддержка всех основных отчётов WB
- **Простота** - 3 строки кода для загрузки любых отчётов

---

## 📊 Поддерживаемые отчёты

| Ключ | Название | Endpoint |
|------|----------|----------|
| `reportDetail` | 📊 Отчёт о реализации (v5) | `/api/v5/supplier/reportDetailByPeriod` |
| `sales` | 💰 Продажи и возвраты | `/api/v1/supplier/sales` |
| `orders` | 📦 Заказы | `/api/v1/supplier/orders` |
| `stocks` | 📦 Остатки | `/api/v1/supplier/stocks` |
| `incomes` | 🚚 Поставки | `/api/v1/supplier/incomes` |
| `antifraud` | 🚫 Самовыкупы | `/api/v1/analytics/antifraud-details` |
| `penalties` | ⚠️ Штрафы | `/api/v1/analytics/warehouse-measurements` |
| `balance` | 💳 Баланс | `/api/v1/account/balance` |
| `region_sales` | 🌍 По регионам | `/api/v1/analytics/region-sale` |
| `excise` | 🏷️ Маркировка | `/api/v1/analytics/excise-report` |

---

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install aiohttp python-dotenv
```

### Базовое использование

```python
from api.multi_report_loader import MultiReportLoader
import os

# API ключ
api_key = os.getenv("WB_API_KEY")

# Создаём загрузчик
loader = MultiReportLoader(api_key)

# Выбираем отчёты
reports = ["reportDetail", "sales", "orders", "stocks", "balance"]

# Загружаем параллельно
results = loader.load_reports_sync(
    report_keys=reports,
    date_from="2025-10-13T00:00:00Z",
    date_to="2025-10-19T23:59:59Z"
)

# Выводим сводку
loader.print_summary(results)

# Сохраняем в файл
from pathlib import Path
loader.save_to_json(results, Path("output/wb_reports.json"))
```

---

## 📖 Примеры использования

### Пример 1: Все отчёты за неделю

```python
from datetime import datetime, timedelta

date_to = datetime.now()
date_from = date_to - timedelta(days=7)

reports = list(MultiReportLoader.ENDPOINTS.keys())  # Все доступные

results = loader.load_reports_sync(
    report_keys=reports,
    date_from=date_from.strftime("%Y-%m-%dT00:00:00Z"),
    date_to=date_to.strftime("%Y-%m-%dT23:59:59Z")
)
```

### Пример 2: Только финансовые отчёты

```python
financial_reports = [
    "reportDetail",  # Детализация с комиссиями, логистикой
    "balance",       # Текущий баланс
    "antifraud",     # Штрафы за самовыкупы
    "penalties"      # Штрафы за габариты
]

results = loader.load_reports_sync(
    report_keys=financial_reports,
    date_from="2025-10-01T00:00:00Z",
    date_to="2025-10-31T23:59:59Z"
)
```

### Пример 3: Склад и логистика

```python
warehouse_reports = [
    "stocks",    # Остатки
    "incomes",   # Поставки
    "orders"     # Заказы
]

results = loader.load_reports_sync(
    report_keys=warehouse_reports,
    date_from="2025-11-01T00:00:00Z"
)
```

---

## 📁 Структура выходного файла

```json
{
  "metadata": {
    "generated_at": "2025-11-18T22:30:15.123456",
    "reports_count": 5,
    "reports_loaded": ["reportDetail", "sales", "orders", "stocks", "balance"]
  },
  "reports": {
    "reportDetail": {
      "name": "Отчёт о реализации (v5)",
      "status": "success",
      "count": 1234,
      "data": [...]
    },
    "sales": {
      "name": "Продажи и возвраты",
      "status": "success",
      "count": 567,
      "data": [...]
    },
    ...
  }
}
```

---

## ⚡ Производительность

**Последовательная загрузка** (обычный requests):
```
5 отчётов × 2 секунды = 10 секунд
```

**Параллельная загрузка** (asyncio + aiohttp):
```
5 отчётов параллельно = 2-3 секунды
```

**Ускорение: 3-5x** 🚀

---

## 🔧 Интеграция с существующим кодом

### В CLI (cli/main.py)

```python
from api.multi_report_loader import MultiReportLoader

def load_multiple_reports():
    """Новая опция меню: загрузка нескольких отчётов."""
    Config.validate()
    
    loader = MultiReportLoader(Config.WB_API_KEY)
    
    # Выбор отчётов
    print("\nДоступные отчёты:")
    for i, key in enumerate(loader.ENDPOINTS.keys(), 1):
        print(f"{i}. {loader.ENDPOINTS[key]['name']}")
    
    choice = input("\nВыберите (через запятую, или 'all'): ")
    
    if choice.lower() == 'all':
        reports = list(loader.ENDPOINTS.keys())
    else:
        indices = [int(x.strip()) for x in choice.split(',')]
        reports = [list(loader.ENDPOINTS.keys())[i-1] for i in indices]
    
    # Даты
    date_from = Prompts.get_string_input("Дата начала", "2025-10-13T00:00:00Z")
    date_to = Prompts.get_string_input("Дата окончания", "2025-10-19T23:59:59Z")
    
    # Загружаем
    results = loader.load_reports_sync(reports, date_from, date_to)
    loader.print_summary(results)
    
    # Сохраняем
    output_file = Config.OUTPUT_DIR / f"wb_multi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    loader.save_to_json(results, output_file)
    
    return results
```

---

## 🧪 Тестирование

```bash
# Запустить пример
python examples/multi_report_example.py

# Или напрямую
python -m api.multi_report_loader
```

---

## 📝 Расширение новыми отчётами

Добавьте новый endpoint в `MultiReportLoader.ENDPOINTS`:

```python
ENDPOINTS = {
    # ... существующие отчёты
    
    "new_report": {
        "name": "Название отчёта",
        "url": "https://statistics-api.wildberries.ru/api/v1/your/endpoint",
        "params_builder": lambda df, dt: {"dateFrom": df, "dateTo": dt}
    }
}
```

---

## 🛡️ Обработка ошибок

Каждый отчёт загружается независимо:
- Если один отчёт упал — остальные загрузятся
- Ошибки сохраняются в результат с описанием
- HTTP коды и текст ошибок доступны для анализа

```python
# Проверка результатов
for key, result in results.items():
    if result["status"] == "error":
        print(f"❌ {result['name']}: {result['error']}")
    else:
        print(f"✅ {result['name']}: {result['count']} записей")
```

---

## 💡 Советы

1. **Rate limits** - WB API ограничивает ~1 запрос/минуту на endpoint
2. **Период данных** - некоторые отчёты хранят данные только 90 дней
3. **Размер лимита** - для `reportDetail` используйте `limit=100000` для больших периодов
4. **Формат дат** - всегда RFC3339: `2025-10-13T00:00:00Z`

---

## 🔗 Связанные файлы

- `api/wb_client.py` - Базовый WB API клиент
- `api/multi_report_loader.py` - Мультирепортер
- `examples/multi_report_example.py` - Примеры использования
- `docs/WB_API_COMPLETE.md` - Полная документация WB API
# 🔌 WB API Integration

## Поддерживаемые эндпоинты

### 1. Получение данных о продажах

**Endpoint:** `/api/v1/supplier/reportDetailByPeriod`

**Метод:** GET

**Параметры:**
- `dateFrom` - Дата начала (YYYY-MM-DD)
- `dateTo` - Дата окончания (YYYY-MM-DD)
- `nmId` - Фильтр по товару (опционально)

**Пример запроса:**
```python
from api.wb_client import WBAPIClient

client = WBAPIClient(api_key="your_key")
data = client.get_sales(
    date_from="2024-01-01",
    date_to="2024-12-31",
    nm_id=432695539
)
```

### 2. Получение данных о хранении

**Endpoint:** `/api/v1/supplier/reportSales`

**Метод:** GET

**Параметры:**
- `dateFrom` - Дата начала
- `dateTo` - Дата окончания

**Пример запроса:**
```python
storage_data = client.get_storage_data(
    date_from="2024-01-01",
    date_to="2024-12-31"
)
```

## Аутентификация

Все запросы требуют заголовок:

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Обработка ошибок

```python
try:
    data = client.get_sales("2024-01-01", "2024-12-31")
except Exception as e:
    print(f"Ошибка API: {e}")
```

## Rate Limits

- **Запросы:** до 100 запросов в минуту
- **Timeout:** 30 секунд

## Полезные ссылки

- [Официальная документация WB API](https://openapi.wildberries.ru)
- [Панель продавца](https://seller.wildberries.ru)
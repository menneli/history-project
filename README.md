```markdown
# HistorySounds

FastAPI веб-приложение, связывающее музыку XX века с историческими событиями. Данные импортируются из Excel, хранятся в SQLite и отображаются через Jinja2 шаблоны с полной поддержкой кириллических URL.

> Проект полностью self-hosted и развёрнут на Railway: [history-project-production.up.railway.app](https://history-project-production.up.railway.app)

## Требования
- Python 3.10+

## Быстрый старт
1. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

2. **Импортируйте и свяжите данные**
   ```bash
   python main.py
   ```
   *Создаёт `data/hs.db`, импортирует ~50 валидных композиций и 221 событие, связывая их через колонку `ID события`.*

3. **Запустите веб-сервер**
   ```bash
   uvicorn app:app --reload
   ```
   Откройте: `http://localhost:8000`

## Чек-лист проверки
| Тест | Ожидаемый результат                                                            |
|------|--------------------------------------------------------------------------------|
| **Таймлайн загружается** | Показывает 221 событие, без `nan` или пустых записей                           |
| **Клик по событию** | Открывает детали с связанными музыкальными произведениями                      |
| **Кириллические URL** | Корректно обрабатывает названия вроде `«День Победы»`                          |
| **Связи отображаются** | У событий с композициями появляется секция "Связанные произведения"            |
| **Нет проблем с кэшем** | Жёсткое обновление (`Ctrl+Shift+R` или `Ctrl+F5`) показывает актуальный контент |

## Структура проекта
```
history-project/
├── main.py              # Настройка БД и пайплайн импорта из Excel
├── app.py               # FastAPI веб-сервер (маршруты + Jinja2 шаблоны)
├── config.py            # Загрузчик настроек/переменных окружения
├── data/
│   ├── hs.db            # SQLite база данных (создаётся автоматически)
│   └── history_sounds.xlsx  # Исходные данные
├── templates/           # Jinja2 HTML шаблоны
├── static/              # CSS/JS/ассеты
├── models/              # SQLAlchemy модели (Song, Event, association)
├── services/            # Импортер и парсер Excel
└── requirements.txt     # Зависимости
```

## Решение проблем
| Проблема | Решение |
|----------|---------|
| `jinja2 must be installed` | `python -m pip install jinja2` |
| `304 Not Modified` / CSS не загружается | Жёсткое обновление (`Ctrl+Shift+R`) или режим инкогнито |
| `nan` или пустые строки | Перезапустите `python main.py` — импортёр фильтрует пустые строки |
| Порт 8000 занят | Используйте `uvicorn app:app --port 8080` |

---

# HistorySounds

FastAPI web application linking 20th-century music with historical events. Data is imported from Excel, stored in SQLite, and rendered via Jinja2 templates with full Cyrillic/UTF-8 URL support.

> Fully self-hosted and deployed on Railway: [history-project-production.up.railway.app](https://history-project-production.up.railway.app)

## Requirements
- Python 3.10+

## Quick Start
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Import and link data**
   ```bash
   python main.py
   ```
   *Creates `data/hs.db`, imports ~50 valid tracks and 221 historical events, linking them via the `Event ID` column.*

3. **Start the web server**
   ```bash
   uvicorn app:app --reload
   ```
   Open: `http://localhost:8000`

## Verification Checklist
| Test | Expected Result                                               |
|------|---------------------------------------------------------------|
| **Timeline loads** | Shows 221 events, no `nan` or empty entries                   |
| **Click on an event** | Opens details with related musical compositions               |
| **Cyrillic URLs** | Handles titles like `«День Победы»` correctly                 |
| **Links display** | Events with tracks show a "Related Compositions" section      |
| **No cache issues** | Hard refresh (`Ctrl+Shift+R` or `Ctrl+F5`) shows fresh content |

## Project Structure
```
history-project/
├── main.py              # DB setup + Excel import pipeline
├── app.py               # FastAPI web server (routes + Jinja2 templates)
├── config.py            # Settings / env variable loader
├── data/
│   ├── hs.db            # SQLite database (auto-created)
│   └── history_sounds.xlsx  # Source data
├── templates/           # Jinja2 HTML templates
├── static/              # CSS/JS/assets
├── models/              # SQLAlchemy models (Song, Event, association)
├── services/            # Excel importer and parser
└── requirements.txt     # Project dependencies
```

## Troubleshooting
| Issue | Solution |
|-------|----------|
| `jinja2 must be installed` | Run `python -m pip install jinja2` |
| `304 Not Modified` / CSS not loading | Hard refresh (`Ctrl+Shift+R`) or incognito mode |
| `nan` or empty rows | Re-run `python main.py` — importer filters empty Excel rows |
| Port 8000 busy | Use `uvicorn app:app --port 8080` |

---
*Built with FastAPI, SQLAlchemy, Jinja2, and pandas. Data pipeline handles Excel edge cases: NaNs, quotes, float IDs, empty rows.*
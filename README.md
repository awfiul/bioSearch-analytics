# bioSearch-analytics

Программная система для обработки, анализа и визуализации результатов поиска
биологических последовательностей BLAST.

## Текущий статус

Подготовлен базовый каркас проекта и окружение для дальнейшей реализации:

- Streamlit-точка входа `app.py`;
- структура модулей `src/`;
- примеры входных файлов `data/examples/`;
- базовый тест структуры проекта;
- список зависимостей `requirements.txt`.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

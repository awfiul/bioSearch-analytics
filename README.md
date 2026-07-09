# bioSearch-analytics

Программная система для обработки, анализа и визуализации результатов поиска
биологических последовательностей BLAST.

Проект не реализует алгоритм BLAST. Он работает с готовыми результатами BLAST,
приводит их к единой таблице, позволяет фильтровать данные, строить графики,
проводить исследовательский анализ и экспортировать результаты.

## Возможности

- загрузка файлов BLAST XML, TSV, TXT и TAB;
- автоматическое определение формата входного файла;
- парсинг BLAST XML через Biopython;
- парсинг BLAST tabular output `outfmt 6`;
- унификация данных в общий DataFrame;
- сводная статистика по результатам;
- интерактивная фильтрация;
- таблица результатов с выбором отображаемых колонок;
- графики на Plotly;
- исследовательский анализ;
- экспорт CSV, Excel и HTML-отчета;
- тесты основной логики.

## Используемые технологии

- Python
- Streamlit
- Biopython
- pandas
- numpy
- plotly
- matplotlib
- openpyxl
- pytest

## Установка

Проект рассчитан на запуск под Windows.

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Если используется `cmd.exe`:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Запуск

```powershell
streamlit run app.py
```

После запуска Streamlit откроет приложение в браузере.

## Пример использования

1. Запустить приложение.
2. В левой панели загрузить файл из `data/examples/`.
3. Проверить блоки с информацией о файле и определенным форматом.
4. Посмотреть сводную статистику.
5. Применить фильтры в левой панели.
6. Изучить графики и исследовательский анализ.
7. Скачать CSV, Excel или HTML-отчет.

Примеры файлов:

- `data/examples/sample_blast.tsv`
- `data/examples/sample_blast.xml`

## Поддерживаемые входные форматы

### BLAST XML

Файл с расширением `.xml`, содержащий структуру BLAST XML:

```text
<BlastOutput>
  ...
</BlastOutput>
```

### BLAST tabular

Файл с расширением `.tsv`, `.txt` или `.tab`.

Поддерживается стандартный порядок колонок BLAST `outfmt 6`:

```text
qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore
```

Файл может быть с заголовком или без него.

## Единая схема данных

После парсинга XML и tabular приводятся к общей схеме:

```text
query_id
hit_id
hit_description
evalue
bitscore
score
identity_percent
alignment_length
query_start
query_end
hit_start
hit_end
gaps
coverage
source_format
```

## Фильтры

В приложении доступны фильтры:

- `E-value <=`;
- `identity >=`;
- `bitscore >=`;
- `alignment_length >=`;
- `Top N` по bitscore;
- поиск по query, hit или описанию.

## Визуализации

Реализованы графики:

- распределение `-log10(E-value)`;
- распределение `identity_percent`;
- top hits по `bitscore`;
- scatter plot `identity_percent vs bitscore`;
- scatter plot `alignment_length vs bitscore`;
- влияние порога `E-value` на количество результатов;
- количество результатов до и после фильтрации.

## Исследовательский анализ

Приложение автоматически рассчитывает:

- влияние разных порогов E-value;
- корреляцию между `bitscore` и `identity_percent`;
- корреляцию между `alignment_length` и `bitscore`;
- эффективность комбинированного фильтра:

```text
E-value <= 1e-5
identity_percent >= 70
alignment_length >= 50
```

Также формируются краткие текстовые выводы.

## Экспорт

Доступны форматы:

- CSV: `filtered_blast_results.csv`;
- Excel: `filtered_blast_results.xlsx`;
- HTML-отчет: `blast_analysis_report.html`.

В HTML-отчет включаются:

- имя файла;
- дата анализа;
- примененные фильтры;
- сводная статистика;
- top-10 результатов;
- краткие исследовательские выводы.

## Тестирование

Запуск всех тестов:

```powershell
.\venv\Scripts\Activate.ps1
python -m pytest
```

Проверка компиляции Python-файлов:

```powershell
python -m compileall app.py src tests
```

## Структура проекта

```text
bioSearch-analytics/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── examples/
│       ├── sample_blast.tsv
│       └── sample_blast.xml
├── src/
│   ├── analysis/
│   │   ├── filtering.py
│   │   ├── research.py
│   │   └── statistics.py
│   ├── export/
│   │   ├── csv_exporter.py
│   │   ├── excel_exporter.py
│   │   └── html_report.py
│   ├── parsers/
│   │   ├── blast_tabular_parser.py
│   │   ├── blast_xml_parser.py
│   │   ├── format_detector.py
│   │   └── schema.py
│   ├── utils/
│   │   └── table_display.py
│   └── visualization/
│       └── charts.py
└── tests/
    ├── test_blast_tabular_parser.py
    ├── test_blast_xml_parser.py
    ├── test_filtering.py
    ├── test_statistics.py
    └── ...
```

## Ограничения

- приложение не запускает BLAST, а анализирует уже готовые результаты;
- HMMER пока не поддерживается;
- PDF-экспорт пока не реализован;
- HTML-отчет не включает интерактивные графики;
- для больших файлов производительность зависит от объема данных и памяти машины.

## Возможные дальнейшие улучшения

- поддержка HMMER;
- сравнение двух BLAST-файлов;
- PDF-отчет;
- запуск локального BLAST из интерфейса;
- поддержка нескольких загруженных файлов;
- кластеризация результатов;
- интерактивная карта выравниваний;
- сохранение истории анализов.

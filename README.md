# Демоурок · StarRocks 4.1

Две таблицы содержат одни и те же 131 072 события. В каждой по 16 tablets. Один фильтр оставляет движку 1 tablet в первой раскладке и все 16 во второй. Предскажите, что произойдёт, когда клиент вместо даты и арендатора пришлёт только event_id. Проверьте прогноз в плане FE и посмотрите, что выполнил BE.

**Инструменты:** StarRocks 4.1.4 · Docker Compose · Python 3.14 · uv · VS Code · DataGrip.

[Подготовка рабочего места](START.md) · [Слайды демоурока (PDF)](weeks/01/01/slides.pdf)

## Пройти демоурок

[Куда исчезли 15 из 16 tablets?](weeks/01/01/README.md)

После настройки запустите команды из корня репозитория. В DataGrip откройте SQL-консоль из инструкции. После разбора выполните задания в демоуроке.

```sh
uv sync --locked
uv run python lab.py up 01/01
uv run python lab.py setup 01/01
uv run python lab.py run 01/01
uv run python weeks/01/01/run.py --profile
uv run python lab.py check 01/01
uv run python lab.py down 01/01
```

В полном курсе 12 недель. Дальше вы разберёте путь записи через Stream Load и Kafka, выбор плана CBO, профили pipeline, обновление MV, внешние сканирования Iceberg, маршрутизацию нагрузки и векторный поиск.

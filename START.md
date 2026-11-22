# Рабочее место и первый запуск

Установите Docker с Compose v2.20.0 или новее, VS Code с расширением Python, DataGrip и uv. Проверьте `docker compose version`, `docker info` и `uv --version`. Для базового стенда разумно выделить Docker 6–8 ГБ, для Iceberg или локальной модели — больше. Это ориентир для ноутбука. Первый запуск скачивает образы. Полноценный стенд одного урока занимает один набор локальных портов.

1. Откройте корень репозитория в VS Code. В терминале выполните команды ниже. Через **Python: Select Interpreter** выберите Python 3.14 из локальной `.venv` (в Windows — `.venv/Scripts/python.exe`).
2. В DataGrip откройте **File → New → Data Source → MySQL**. Хост `127.0.0.1`, порт `9030`, логин `root`, пароль пустой для этого стенда. Загрузите недостающий JDBC-драйвер и нажмите **Test Connection**. Базу `sr01` выберите после setup. Другой поддерживаемый вариант — нативный JDBC-драйвер StarRocks. В комплекте SQL работает через MySQL-протокол.
3. Сохраните свою работу в отдельном файле, исполняйте выделенный запрос в DataGrip. В SQL-консоли выполните `SELECT current_version();` и `SHOW BACKENDS;`. Версия должна быть 4.1.4, у бэкенда — Alive=true. Один FE и один BE размещены в одном контейнере, поэтому replication_num=1. Уроки про отказоустойчивость прямо указывают, что проверяется на этом масштабе.

```sh
uv python install 3.14
uv sync --locked
cd lessons/01
docker compose up -d --wait
uv run --project ../.. python ../../tools/lab.py setup
```

Первое задание — в README урока. Сначала решите его в DataGrip. В той же папке проверьте решение. Эталон можно воспроизвести отдельной командой.

```sh
uv run --project ../.. python ../../tools/lab.py check
uv run --project ../.. python ../../tools/lab.py solve
uv run --project ../.. python ../../tools/lab.py check
```

Для перерыва используйте `docker compose stop` и затем `docker compose start`. Перед переходом к следующей папке остановите предыдущий стенд, иначе порт 9030 будет занят. Данные StarRocks находятся в контейнере: `docker compose down` удаляет его и базу урока. После этого следующий `up` и `setup` создадут стенд заново. Для полного удаления дополнительных томов текущего урока предусмотрен `docker compose down -v`. Команда setup пересоздаёт учебные объекты. Все материалы рассчитаны на локальные синтетические данные.

**Диагностика.** Если порт занят, проверьте `docker ps` и остановите свой предыдущий урок. Если Docker сообщает unhealthy, откройте `docker compose logs --tail=120 starrocks`, проверьте свободную память и завершение первой загрузки. Если в DataGrip нет таблиц, выберите схему в настройках Data Source и нажмите Synchronize. Если SELECT работает, но таблицу создать невозможно, проверьте Alive у BE. HTTP-интерфейс FE использует 8030, SQL-клиент — 9030.

[Docker-стенд StarRocks](https://docs.starrocks.io/docs/quick_start/shared-nothing/) · [Ветки и исправления 4.1](https://docs.starrocks.io/docs/release_notes/release-4.1/) · [Подключение DataGrip](https://docs.starrocks.io/docs/integrations/IDE_integrations/DataGrip/) · [Python через uv](https://docs.astral.sh/uv/guides/install-python/)

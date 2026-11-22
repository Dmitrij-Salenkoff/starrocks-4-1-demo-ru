# Рабочее место и первый запуск

Для курса нужны базовые SQL (JOIN, GROUP BY), Python (функции, чтение CSV) и терминал. На первом занятии вы научитесь отличать повтор доставки от второй покупки. Откройте репозиторий целиком в VS Code. Все команды ниже выполняются из его корня.

## Подготовить компьютер

Установите Docker Desktop либо Docker Engine с Compose v2, uv, VS Code с расширением Python и DataGrip. Для первого запуска нужен интернет: Docker скачает образы, uv — интерпретатор и зависимости, DataGrip — JDBC-драйвер. Для планирования начните с 4 vCPU, 8 ГБ памяти Docker и 12 ГБ свободного диска. Для Iceberg и Kafka при нехватке памяти увеличьте лимит Docker. Это ориентиры для практикума. [Docker](https://docs.docker.com/get-started/get-docker/) · [uv](https://docs.astral.sh/uv/getting-started/installation/) · [VS Code](https://code.visualstudio.com/) · [DataGrip](https://www.jetbrains.com/datagrip/)

```sh
docker compose version
docker info
uv python install 3.14
uv sync --locked
uv run python --version
uv run python lab.py list
uv run python lab.py up 01/01
uv run python lab.py setup 01/01
```

В VS Code вызовите **Python: Select Interpreter** и выберите окружение `.venv` в корне репозитория. Стек закреплён в `uv.lock` и каждом `compose.yaml`. Dev-образ 4.1.4 есть под ARM64 и AMD64, включая Mac с Apple Silicon. [Теги образа](https://hub.docker.com/r/starrocks/allin1-ubuntu/tags) · [Как uv использует lock-файл](https://docs.astral.sh/uv/concepts/projects/sync/)

## Подключить DataGrip

В **File → New → Data Source → MySQL** укажите Host `127.0.0.1`, Port `9030`, User `root`, пустой Password и Database `course`. Нажмите **Download missing driver files**, затем **Test Connection**. Назовите источник «StarRocks · локальный курс». Откройте Query Console и выполните запрос ниже. Функция `current_version()` показывает сборку StarRocks. [Драйвер DataGrip](https://www.jetbrains.com/help/datagrip/mysql.html) · [current_version](https://docs.starrocks.io/docs/sql-reference/sql-functions/utility-functions/current_version/)

```sql
USE course;
SELECT current_version(), @@run_mode, DATABASE();
SHOW FRONTENDS;
SHOW BACKENDS;
```

Ожидайте версию 4.1.4 с идентификатором сборки, режим shared_nothing, базу course и живой BE. Каждый новый стенд слушает те же адреса. Закройте старую SQL-консоль и переподключитесь, когда меняете занятие.

## Пройти занятие

1. В `weeks/WW/LL/README.md` прочитайте условие и запишите прогноз до запуска запроса.
2. `up` запускает отдельный Compose-проект. `setup` пересоздаёт учебные таблицы этого занятия. Запустите указанный в занятии Python-драйвер, если он нужен.
3. Откройте `explore.sql` в DataGrip и привяжите его к источнику курса. Выделяйте отдельный запрос и запускайте Cmd+Enter или Ctrl+Enter. Для повторения всего опыта используйте `uv run python lab.py explore 01/01`.
4. Сохраните свои SQL, ожидаемый и фактический вывод в отдельной папке на компьютере. `uv run python lab.py check 01/01` проверяет конкретный инвариант стенда. Письменное решение и остальные результаты оцените по критериям занятия.
5. Завершите занятие командой `uv run python lab.py down 01/01`. Она удаляет контейнеры и тома только выбранного проекта. Перед командой сохраните результаты, которые понадобятся для портфолио.

## Если результат отличается

| Симптом | Что проверить |
|---|---|
| Порт уже занят | Выполните `docker ps`, найдите предыдущий стенд и остановите его штатной командой `down` с его номером. Сторонний сервис на этом порту остановите только если он ваш. |
| DataGrip подключается, CREATE TABLE не проходит | Проверьте `SHOW BACKENDS` и `Alive`. FE может стартовать раньше BE. Команда `lab.py up` ждёт готовности обоих. |
| Стол или база отсутствуют | Выполните `setup` из нужного репозитория. В DataGrip переподключите источник и обновите схему. |
| Не запускается контейнер | Выполните `uv run python lab.py status 01/01` и `uv run python lab.py logs 01/01`. При OOM увеличьте память Docker. После повторного старта запустите setup. |
| При проверке FAIL | Раскройте `check.sql`, выполните внутренний SELECT по частям и найдите первый расходящийся ключ. Сохраните пример до повторного setup. |
| В ошибке DDL есть `backends without enough disk space` | Проверьте доступное дисковое место в Docker Desktop и вывод `SHOW BACKENDS`. BE может быть живым, но не принять новый tablet из-за порога свободного места. Увеличьте диск Docker или освободите место, затем повторите setup. |

Все учётные данные стенда учебные. Порты с пустым локальным паролем привязаны к loopback. Используйте синтетические события из репозитория.

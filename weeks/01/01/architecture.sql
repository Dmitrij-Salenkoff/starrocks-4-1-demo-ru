-- Версия и способ хранения данных в этом стенде.
SELECT current_version() AS starrocks_version, @@run_mode AS run_mode;

-- Кто принимает запросы?
SHOW FRONTENDS;

-- Кто здесь хранит строки и выполняет вычисления?
SHOW BACKENDS;

-- Есть ли отдельные вычислительные узлы (CN)?
SHOW COMPUTE NODES;

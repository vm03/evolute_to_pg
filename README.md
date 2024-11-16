Необходим PostgreSQL с раширениями timescaledb и postgis.

1. Создать БД в PostgreSQL и таблицы из evolute.sql
2. Залогинится на сайте https://app.evassist.ru в приватном(инкогнито) окне браузера
3. Включить режим разработчика и скопирывать из куки в запросе, значения кук `evy-platform-access` и `evy-platform-refresh`
4. Записать их в базу запросом `INSERT INTO token_storage (access_token, refresh_token, updated_at) VALUES ('<evy-platform-access>', '<>evy-platform-refresh', now());`
5. В скриптах поменять настроики базы
6. В режиме разработчика скопировать из пути в запросе id машины `car-service/tbox/<carid>/info`
7. В скрипте заменить id машины
8. Добавить запуск скриптов в крон, примено как в crontab.txt
9. Добавить в графану дашборд grafana.json

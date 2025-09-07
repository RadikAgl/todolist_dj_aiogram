# ToDoList



### Запуск СУБД Postgresql

   ```shell
   docker run --name post_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=todolist -p 5439:5432 -d postgres
   ```


### Запуск брокера сообщений REDIS

   ```shell
   docker run --name redis-db -d -p 6379:6379 redis
   ```

# Запуск Celery

Celery используется для уведомления пользователей в случае наступления времени выполнения задачи. Убедитесь, что виртуальное окружение активировано, и сервер
запущен, затем откройте новое окно терминала и выполните следующие команды:

**Запуск Celery Worker:**

   ```bash
   celery -A config worker --loglevel=INFO

   ```

**Запуск Celery Beat откройте новое окно терминала:**

   ```bash
   celery -A config beat -l info
   ```

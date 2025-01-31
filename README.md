Чтобы развернуть проект Django из GitHub на локальном компьютере, следуй этим шагам:

Сначала открой терминал и клонируй репозиторий, используя команду git clone <URL-репозитория>. Затем перейди в директорию проекта с помощью cd <имя_папки_с_проектом>.

Создай виртуальное окружение с помощью python -m venv venv. Это позволит изолировать зависимости проекта. Активируй виртуальное окружение: на Windows используй venv\Scripts\activate, а на macOS/Linux — source venv/bin/activate.

Установи зависимости, используя файл requirements.txt, с помощью команды pip install -r requirements.txt. 

Создай файл .env и поместите в него:

SECRET_KEY=''
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''

*поля должны быть заполнены

Теперь выполни миграции для настройки базы данных командой python manage.py migrate. Если нужно, создай суперпользователя с помощью команды python manage.py createsuperuser.

Запусти сервер, используя python manage.py runserver. Теперь ты можешь открыть проект в браузере по адресу http://127.0.0.1:8000/.

# library-service

Django Rest Framework project for management of books and borrowings in library

## Features:
* Authentication functionality
* Management of books inventory
* Monitoring of due borrowings
* Notifications via Telegram

## How to run

Project supports sending notification via telegram for various occasions. 
Skip telegram part if you don't need this.

### Create telegram bot

1. Proceed to https://telegram.me/BotFather or search for **BotFather** in your telegram app
2. Click **Start**
3. Type **/newbot** and follow short instructions
4. Receive the bot **token** - store it safely!!!

### Install project

```shell
git clone https://github.com/Vanya2389/library-service.git
cd library-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create .env file in root directory and store there your 
SECRET_KEY, BOT_TOKEN and TELEGRAM_CHAT_ID 
like shown in .env_sample

```
python manage.py migrate
python manage.py loaddata test_data.json
python manage.py runserver
```

### Run with docker
```
docker-compose up --build
```

### Use users
Get token on api/user/token/

Admin
```
email admin@gmail.com
password 123456
```
User
```
email user@gmail.com
password 123456
```

### See our documentation
You can see it on api/doc/swagger/
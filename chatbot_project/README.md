ChatBot

System requirements

Docker Engine 19.03.0+
Docker Compose


Provide Telegram Bot token to the aiogram app
Create the file .tg-bot.env, paste the content of the .tg-bot.example.env in it.
Set the BOT_TOKEN variable in the created file. Get the token from the BotFather bot in Telegram.
Set other needed variables if you want to run the Telegram client app that creates groups
with the user and the bot (because the bot can't initiate a dialog with the user).

Build images and run containers
docker-compose up --build
The backend/bot.py app will create and use directories:


./test_db to store the SQLite database file test.db


./test_bot_data to store message histories for each user who uses the bot


Connect to the tg-client container to let it log in Telegram (optional)
docker attach chatbot_python-tg-client_1
Enter the mobile phone of your Telegram account. Then enter a verification code to login.

Usage


/start to start a dialog with the bot
send the bot an .xlsx file with a caption /add_users to parse the table and load new
users into the database
send the /create_chats command to the Telegram account used to create chats with
the users that have been loaded in the previous step


Edit the dependencies of the react-app
Enter the shell while the react-app container is running (_1 can be different, run docker ps to check it out):
docker exec -it chatbot_react-app_1 sh
Run custom yarn commands. The package.json and yarn.lock files will be updated in your local source code directory if needed by yarn.
Exit the shell with exit.
The node_modules directory can be deleted after the shell session because it isn't actually used within the running container.
Then rebuild the image of react-app. For example, run:
docker-compose up --build
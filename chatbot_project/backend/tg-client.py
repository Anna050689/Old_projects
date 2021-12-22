from os import environ
import traceback

from telethon import TelegramClient, sync, events
from telethon import functions, types
from telethon.tl import functions

from db_worker import SqliteDbWorker


BOT_NAME = environ['BOT_NAME']

db_worker_ = SqliteDbWorker()
# HR, которого нужно будет присоединить к диалогу
HR_PHONE = environ['HR_PHONE']
HR_FIRST_NAME = environ['HR_FIRST_NAME']

contact_initial_message = 'Здравствуйте, {firstName} {lastName}, я представляю компанию EPAM, ' \
                          'где вы посетили один из наших ивентов. Хотелось бы получить ваш фидбек по мероприятию.\n' \
                          'Опрос не займет много Вашего времени и большей частью пройдет в автоматическом режиме.\n' \
                          'После завершения опроса при желании вы сможете продолжить диалог с нашим HR-ом, ' \
                          'который расскажет об открытых вакансиях у нас в данный момент ' \
                          'и сможет более подробно ответить на Ваши вопросы.\n' \
                          'Для запуска бота-опросника напиши в чат команду /start\n' \
                          'Подсказка: также команду можно выбрать с клавиатуры чата ' \
                          '(иконка команд выглядит так: "/")'

client = TelegramClient(
    environ['APP_SESSION_NAME'],
    environ['APP_API_ID'],
    environ['APP_API_HASH']
)

with client:
    my_info = client.get_me()

    dialogs = client.get_dialogs()
    print(my_info.id)

    @client.on(events.NewMessage())
    async def my_event_handler(event):
        chat = await event.get_input_chat()
        sender = await event.get_sender()
        print(chat.chat_id, '->', event)

        if ('/help' in event.raw_text) or ('help' in event.raw_text):
            await event.reply(f'Привет снова! Для запуска бота-опросника напиши в чат команду /start '
                              f'или /start{BOT_NAME}. Подсказка: так же команду можно выбрать'
                              f'с клавиатуры чата (иконка команд выглядит так: "/")')
        elif event.message.message == '/create_chats':
            for i in db_worker_.get_no_telegram_chats():
                print(i)
                try:
                    contact_peer = await client.get_input_entity(i.phone)
                    bot_peer = await client.get_input_entity(BOT_NAME)
                    working_group_title = f'EPAMChat with {i.first_name} {i.last_name}'
                    # print(contact_peer, bot_peer, working_group_title)

                    working_group = await client(functions.messages.CreateChatRequest(
                        users=[contact_peer, bot_peer],
                        title=working_group_title))
                    working_group_id = working_group.chats[0].id  # 370317232
                    print(f'"{working_group_title}" chat started, ID: {working_group_id}')
                    await client.send_message(working_group_id, contact_initial_message.format(
                        firstName=i.first_name, lastName=i.last_name
                    ))
                    db_worker_.set_has_telegram(id_chat=i.id_chat)
                    await client.send_message(
                        my_info.id,
                        f'Contact found: <a href="tg://user?id={str(event.sender_id)}">' +
                        f'{i.first_name} {i.last_name}</a>',
                        parse_mode='html'
                    )
                    # print(res)
                except:
                    # TODO add actions on error
                    traceback.print_exc()
        elif event.message.message == '/add_hr':  # u'Подключаю рекрутера...':
            # TODO 4.1 remove initial message '/add_hr'
            print ('try delete /add_hr')
            await client.delete_messages(event.chat, event.message)
            # 4.2 attach HR contact to group
            hr_contact_peer = await client.get_input_entity(HR_PHONE)
            await client(functions.messages.AddChatUserRequest(
                chat.chat_id,
                hr_contact_peer,
                fwd_limit=100))  # allow the user to see the 100 last messages
            msg_to_send = f'HR "{HR_FIRST_NAME}" added to chat'
            print(msg_to_send)
            await client.send_message(chat.chat_id, msg_to_send)

    client.run_until_disconnected()

from os import environ
import traceback

from aiogram import Bot, Dispatcher, executor, types
import xlrd

from load_state_machine import state_machine
from helpers import set_data, get_data
from db_worker import SqliteDbWorker
from models import InitContact


db_worker_ = SqliteDbWorker()

bot = Bot(token=environ['BOT_TOKEN'])
dp = Dispatcher(bot)

user_dict = {}
chat_with_user = None

db = SqliteDbWorker()


@dp.message_handler(commands=['start', 'get_chat'])
async def start(message: types.Message):
    print('here here')
    chat_id = message.chat.id
    if '/start' in message.text:
        res = set_data(chat_id, new_data={"state": 0, "dialog": ""})
        # TODO add actions on error
        if not res:
            pass
        else:
            await handle_message(message)
    elif '/get_chat' in message.text:
        data = get_data(chat_id)
        print('data', data)
        # TODO add actions on error
        if data:
            # bot.send_message(chat_id, data["dialog"])
            await bot.send_message(chat_id, data["dialog"])
        else:
            pass


@dp.message_handler()
async def handle_message(message: types.Message):
    print('here')
    chat_id = message.chat.id
    cur_data = get_data(chat_id)
    # cur_state = get_state(chat_id)
    print('cur_data', cur_data)
    if cur_data:
        frame = state_machine.get_next_frame(cur_data["state"], condition=message.text)
        print('frame', frame)

        if frame:
            msg_to_send = frame.frame_message

            if frame.frame_elems:
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add(*[elem.frame_elem_text for elem in frame.frame_elems])
            else:
                markup = types.ReplyKeyboardRemove()

            # bot.send_message(chat_id, msg_to_send, reply_markup=markup)
            await message.answer(msg_to_send, reply_markup=markup)

            cur_data["state"] = frame.id_frame
            cur_data["dialog"] += f"Ответ: {message.text}\n"
            cur_data["dialog"] += f"Бот: {msg_to_send}\n"

            res = set_data(chat_id, new_data=cur_data)
            # TODO add actions on error
            if not res:
                pass


# all files handling
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def start(message: types.message.Message):
    async def get_sheet(file_id) -> xlrd.sheet.Sheet:
        file = await bot.get_file(file_id)
        content = await file.download()
        xl_workbook = xlrd.open_workbook(content.name)
        return xl_workbook.sheet_by_index(0)

    print('handle document', message.caption)

    if '/add_users' == message.caption:
        try:
            print('file handling')
            if message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                xl_sheet = await get_sheet(file_id=message.document.file_id)

                has_error = False
                with db_worker_.transaction() as c:
                    for row_idx in range(1, xl_sheet.nrows):
                        row = xl_sheet.row(row_idx)
                        contact = InitContact(first_name=row[0].value, last_name=row[1].value,
                                              phone=row[4].value, email=row[2].value)
                        dialog = db_worker_.insert_user(contact, cursor=c)
                        print('dialog', dialog)
                        if not dialog:
                            has_error = True

                    if has_error:
                        await message.reply("Partly uploaded")
                        raise
                    else:
                        await message.reply("Successfully uploaded")
        except:
            traceback.print_exc()
            await message.reply("Error")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)



import pickle


def get_data(chat_id: int) -> dict:
    try:
        with open(f'/test_data/{chat_id}.pickle', 'rb') as db:
            data = pickle.load(db)
            return data
    except OSError:
        return dict()


def set_data(chat_id: int, new_data: dict) -> bool:
    print('set', chat_id, new_data)
    # all_data[chat_id] = value
    # print(all_data)
    with open(f'/test_data/{chat_id}.pickle', 'wb') as db:
        try:
            pickle.dump(new_data, db)
            return True
        except:
            # тут желательно как-то обработать ситуацию
            return False

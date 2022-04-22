import hashlib
from loguru import logger
import requests


# TODO соль в конфиг
SALT = "BDD8ED61A39C9DC8062383B862A56457C27F095BFBEF1F40F6F3BAC97368DBC3"
API_SERVER = "https://stfpmi.ru/api"
# TODO токен в .env
"""
Для 5Б: 4388c9f38310d2dba25cbb5f0d4c0b8c9d96909d855d882beee91084203e0525

Для 6Б: 534acad8324209dc8de2184240bd7868d5a9a4280a5a1e97aa6211b7fa64a6b1
"""
# TOKEN = "4388c9f38310d2dba25cbb5f0d4c0b8c9d96909d855d882beee91084203e0525"  # PROD замок 5Б
# TOKEN = "534acad8324209dc8de2184240bd7868d5a9a4280a5a1e97aa6211b7fa64a6b1"  # PROD замок 6Б
# TOKEN = "7cf97feb2ab1939918c92043ef6dfe34428844a51c7ceee94f90b44549c286a4"  # это дев
# TODO итерации в конфиг
NUM_ITERATIONS = 3


def enhash_rfid_card_id(card_id):
    # This function is used 2 times:
    # First one - on lock-side to enhash real card label, before sending to server
    # Second one - on server-side, before storing in database
    # So total amount of iterations = RFID_CARD_PASS_ITERATIONS * 2
    card_id = card_id.lower()
    card_id += SALT
    for i in range(NUM_ITERATIONS):
        card_id = hashlib.sha256(card_id.encode()).hexdigest()
    return card_id


def allowed_to_unlock(uid_str):
    """Проверка, разрешено ли заходить.

    Возвращает кортеж из соображений совместимости со старым сайтом.
    """
    # convert to hex format
    logger.debug(f"converting {uid_str} to hex")

    card_1, card_2, card_3, card_4 = [int(i) for i in uid_str.split('.')]
    hex_uid = f"{format(card_1, '02x').upper()}{format(card_2, '02x').upper()}{format(card_3, '02x').upper()}{format(card_4, '02x').upper()}"
    logger.debug(f"converting {hex_uid} to hash")
    uid_hash = enhash_rfid_card_id(hex_uid)
    logger.debug(f"requesting {API_SERVER} to unlock")
    r = requests.post(f'{API_SERVER}/lock', json={'token': TOKEN, 'card_id': uid_hash}, timeout=10)
    if r.status_code != 200:
        logger.info(f"DENIED на карту {hex_uid}")
        return False, "no_orders"
    logger.info(f"GRANTED на карту {hex_uid}")
    return True, "success"


if __name__ == '__main__':
    print(allowed_to_unlock("170.187.204.221"))

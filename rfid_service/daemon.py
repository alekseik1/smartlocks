from multiprocessing import Lock

import requests
from loguru import logger

from device_manager import RfidReader
from door_service.daemon import CONTROL_PORT
from fpmi_client import allowed_to_unlock as fpmi_allowed_to_unlock


def uid_to_str(uid):
    # MIFARE CLASSIC
    try:
        return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])
    except IndexError as e:
        rv = "9.9.9.9"
        logger.error(f"incorrect UID={uid}, with error={e} returning {rv}")
        return rv


def hardcoded_allowed_to_unlock(uid_str):
    file = "admin_uid.txt"
    try:
        with open(file, "r") as f:
            for line in f.readlines():
                if uid_str == line.split()[0].strip():
                    return True
    except FileNotFoundError as e:
        logger.error(f"File {file} not found, returning False. Error: {e}")
    except IndexError as e:
        logger.error(f"File {file} is corrupted, returning False. Error: {e}")
    return False


def main():
    rfid_reader = RfidReader(Lock())
    while True:
        err, uid = rfid_reader.wait_card()
        uid_str = uid_to_str(uid)
        logger.info("processing detected card: {}".format(uid_str))

        # status, cause = allowed_to_unlock(uid_str)
        # УБИРАЕМ проверку от старого сервера, только хардкоденный список
        status = hardcoded_allowed_to_unlock(uid_str)
        logger.info("got result to unlock: {}".format(str(status)))
        if not status:
            # если не админ, то делаем проверку на ФПМИ-сервер
            status_1, cause_1 = fpmi_allowed_to_unlock(uid_str)
            if status_1:
                logger.info("FPMI status_1 IS TRUE, OPENING")
            status = status_1
        if status:
            r = requests.get(f"http://localhost:{CONTROL_PORT}/unlock")
            if r.status_code != 200:
                logger.error(f"open request error, text={r.text}")
        logger.info("(DONE) processing detected card: {}".format(uid_str))


if __name__ == "__main__":
    main()

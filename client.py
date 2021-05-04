import time
import json
import random
import datetime
from subprocess import check_output
from threading import Thread

import requests

from http_lib import lst
from loguru import logger
from device_manager import manager

config = {}


def get_ip():
    return check_output(['hostname', '--all-ip-addresses'])


def configure(filename):
    try:
        logger.info(f'reading config: {filename}')
        with open(filename) as f:
            data = json.load(f)
        logger.debug(f'read data: {data}')
        if (data.get(u'url_unlock') == None) or (data.get(u'url_upd') == None):
            raise ValueError('Invalid content of config file')
    except Exception as e:
        logger.critical(f'error processing config: {e}')
        manager.lcd_display.print_lcd('Configuration error')
    else:
        global config
        config = data
        logger.debug(f"new configuration: {config}")


def allowed_by_server(uid):
    logger.info(f'checking if {uid} is allow by server')
    try:
        global config, ser1, ser2, ser3
        url = config[u'url_unlock'] + uid
        logger.info(f'requesting server URL={url}')
        r = requests.get(url)
        logger.info(f'got response {r.status_code} with text: {r.text}')

        if r.status_code != 200:
            raise requests.HTTPError('Server error')
        # Legacy server answers
        if r.text == 'yes':
            return True, "not_defined"
        if r.text == "no":
            return False, "not_defined"

        resp = json.loads(r.text)
        logger.info(f"name: {resp['name']}")
        logger.info(f'(DONE) checking if {uid} is allow by server')
        if resp["status"] == "yes":
            return True, resp["cause"]
        else:
            return False, resp["cause"]

    except requests.RequestException as e:
        logger.error(f'request error: {e}')
        manager.lcd_display.print_lcd('Network error')
        return False, "error"


def allowed_by_list(uid):
    try:
        logger.info("loading local access_list.txt")
        with open('access_list.txt') as f:
            data = json.load(f, object_hook=date_hook)
        logger.info("(DONE) loading local access_list.txt")

        for o in data:
            if (o['uid'] == uid) \
                    and (o['date_start'].date() == datetime.date.today()) \
                    and (o['time_start'].time() <= datetime.datetime.now().time()) \
                    and (o['time_end'].time() >= datetime.datetime.now().time()):
                logger.info(f"found access record for name: {o['name']}")
                return True
    except OSError as e:
        manager.lcd_display.print_lcd('Database error')
        logger.error("error processing access list: {e}")
        update_list()
    logger.info("fallback to default no access")
    return False


def allowed_by_admin(uid):
    try:
        logger.info(f'looking up uid={uid} in admin list')
        with open('admin_uid.txt', 'rb') as f:
            for line in f:
                if uid == line[:-1]:
                    logger.info(f'found uid={uid} in admin list!')
                    return True
    except IOError as e:
        manager.lcd_display.print_lcd('Local error')
        logger.error(f"error processing admin list {e}")
    return False


def allowed_by_random(p):
    if random.random() < p:
        return True
    return False


def read_one_time_set():
    try:
        logger.info("loading one time set")
        with open("one_time_set", "rb") as f:
            res = set(json.load(f))
        logger.info("(DONE) loading one time set")
        return res
    except IOError as e:
        logger.error(f"one time set reading failure: {e}")
        return set()


def write_one_time_set(set):
    try:
        logger.info("writing one time set")
        with open("one_time_set", "w") as f:
            json.dump(list(set), f)
        logger.info("(DONE) writing one time set")
    except IOError as e:
        logger.error(f"writing failed: {e}")


def allowed_to_unlock(uid):
    logger.info(f'checking if allowed to unlock, uid={uid}')
    if uid in lst:
        return True, "because"
    if allowed_by_admin(uid):
        logger.info('allowed, is admin')
        return True, "admin"

    one_time_set = read_one_time_set()

    if allowed_by_list(uid):
        if not uid in one_time_set:
            one_time_set.add(uid)
            write_one_time_set(one_time_set)
        logger.info('allowed, in local access_list.txt list')
        return True, "list"

    status, cause = allowed_by_server(uid)
    if status:
        if not uid in one_time_set:
            one_time_set.add(uid)
            write_one_time_set(one_time_set)
        logger.info(f'allowed, server response: {cause}')
        return True, cause

    if uid in one_time_set:
        one_time_set.remove(uid)
        write_one_time_set(one_time_set)
        logger.info(f'allowed, last enter')
        return True, "last_time"

    if allowed_by_random(0.05):
        logger.info(f'allowed, by random :)')
        return True, "random"

    logger.info(f'denied, fallback')
    return False, cause


def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d")
        except:
            pass
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%H:%M")
        except:
            pass
    return json_dict


def update_list():
    logger.info('trying to update access list from server')
    try:
        global config
        url = config[u'url_upd']
        logger.debug(f'sending request to {url}')
        r = requests.get(url)
        logger.debug(f'got response: {r.status_code}')
        if r.status_code != 200:
            raise requests.HTTPError('Server error')
        logger.info('successfully fetched access list from server')
        data_str = r.text.replace('\'', '\"')
        data = json.loads(r.text, object_hook=date_hook)
        logger.info('writing server response to access_list.txt')
        with open('access_list.txt', 'w') as f:
            f.write(data_str)
        logger.info('(DONE) writing server response to access_list.txt')
        return data
    except requests.RequestException as e:
        manager.lcd_display.print_lcd('Network error')
        logger.error(f"error asking server to update: {e}")
    except KeyError as e:
        logger.error(f'{e}')
    except Exception as e:
        logger.critical(f'unknown exception: {e}')
    return None


class update_thread(Thread):
    def __init__(self):
        logger.debug('init access_list update thread')
        Thread.__init__(self)
        self.name = "list update thread"
        logger.debug('(DONE) init access list update thread')

    def run(self):
        configure("config.txt")
        while 1:
            logger.info("calling access list update")
            update_list()
            logger.info("(DONE) calling access list update")
            time.sleep(15 * 60)


update_thr = update_thread()

import requests
import json, string, datetime
import sys
import random
from lcd_lib import *
import time
from threading import Thread
from http_lib import *
from subprocess import check_output
from log_writing import*
config = {}

def get_ip():
	return check_output(['hostname', '--all-ip-addresses'])

def configure(filename):
	try:
		with open(filename) as f:
			data = json.load(f)
		if (data.get(u'url_unlock') == None) or (data.get(u'url_upd') == None) :
			raise Exception('Invalid content of config file')
	except:
		print_lcd('Configuration error')
		print_log("Error processing config file: " + str(sys.exc_info()))
		print_log("Continuing working in an old way")
	else:
		global  config
		config = data
		print_lcd('Configured')
		print_log("New configuration: " + str(config)) 

def allowed_by_server(uid):
	try:
		global config, ser1, ser2, ser3
		url = config[u'url_unlock'] + uid
		r = requests.get(url)
		print_log('Unlock request:' + str(url))
		print_log('response status code: ' + str(r.status_code))
		print_log(r.text)

		if r.status_code != 200:
			raise Exception('Server error')
		if (r.text == 'yes'):
			return (True, "not_defined")
		if (r.text == "no") :
			return (False, "not_defined")

		resp = json.loads(r.text)
		print_log("name: " + resp["name"])
		if resp["status"] == "yes":
			return (True, resp["cause"])
		else:
			return (False, resp["cause"])

	except:
		print_lcd('Network error')
		print_log("Error asking server to unlock: " + str(sys.exc_info()))
		print_log("Continuing working")
	return (False, "error")

def allowed_by_list(uid):
	print_log("Asking list")
	try:
		with open('access_list.txt') as f:
			data = json.load(f, object_hook=date_hook)

		for o in data:
			if (o['uid'] == uid)\
			and (o['date_start'].date() == datetime.date.today())\
			and (o['time_start'].time() <= datetime.datetime.now().time())\
			and (o['time_end'].time() >= datetime.datetime.now().time()):
				print_log("access granted")
				print_log("name: " + o["name"])
				return True
	except:
		print_lcd('Database error')
		print_log("Error processing access list: " + str(sys.exc_info()))
		update_list()
	print_log("no access")
	return False

def allowed_by_admin(uid):
	try:
		with open('admin_uid.txt', 'rb') as f:
			for line in f:
				if uid == line[:-1]:
					print_log("Welcome, Admin Adminovich")
					return True
	except:
		print_lcd('Local error')
		print_log("Error processing admin list" + str( sys.exc_info()))
	return False

def allowed_by_random(p):
	if random.random() < p:
		return True
	return False

def read_one_time_set():
	print_log("reading one time set")
	try:
		f = open("one_time_set", "rb")
		res = set(json.load(f))
		f.close()
		print_log("reading ok")
		return res
	except:
		print_log("one time set reading falure " + str(sys.exc_info()))
		return set()

def write_one_time_set(set):
	print_log("writing one time set")
	try:
		f = open("one_time_set", "wb")
		json.dump(list(set), f)
		print_log("writing ok")
	except:
		print_log("writing failed " + str(sys.exc_info()))


def allowed_to_unlock(uid):
	if uid in lst: return (True, "because")
	if allowed_by_admin(uid):
		return (True, "admin")

	one_time_set = read_one_time_set()

	if allowed_by_list(uid):
		if not  uid in one_time_set:
			one_time_set.add(uid)
			write_one_time_set(one_time_set)
		return (True, "list")

	status, cause = allowed_by_server(uid)
	if status:
		if not  uid in one_time_set:
			one_time_set.add(uid)
			write_one_time_set(one_time_set)
		return (True, cause)

	if uid in one_time_set:
		one_time_set.remove(uid)
		write_one_time_set(one_time_set)
		return (True, "last_time")

	if allowed_by_random(0.05):
		return (True, "random")

	return (False, cause)

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
	try:
		global config
		url = config[u'url_upd']
		r = requests.get(url)
		print_log('Update request:' + url)
		print_log('response status code: ' + str(r.status_code))
		if r.status_code != 200:
			raise Exception('Server error')
		json_str = string.replace(r.text, "'", '"')
		with open('access_list.txt', 'w') as f:
			f.write(json_str)
		print_log("Access list successfully updated")
		data = json.loads(json_str, object_hook=date_hook)
		return data
	except:
		print_lcd('Network error')
		print_log("Error asking server to update: " + str(sys.exc_info()))
		print_log("Continuing working")
	return None


class update_thread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.name = "list update thread"

	def run(self):
		configure("config.txt")
		while 1:
			print_log(">->->->->LIST UPDATE EVENT<-<-<-<-<")
			update_list()
			print_log("<-<-<-<-<LIST UPDATE EVENT>->->->->\n")
			time.sleep(15 * 60)

update_thr = update_thread()


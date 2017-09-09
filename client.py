import requests
import json, string, datetime
import sys
import lcd_lib
from http_lib import *

config = {}

def configure(filename):
	try:
		with open(filename) as f:
			data = json.load(f)
		if (data.get('url_unlock') == None) or (data.get('url_upd') == None) :
			raise Exception('Invalide content of config file')
		update_list()
	except:
		lcd_lib.print_lcd('Configuration error')
		print "Error processing config file: ", sys.exc_info()
		print "Continuing working in an old way"
	else:
		global  config
		config = data
		lcd_lib.print_lcd('Configured')
		print "New configuration: ", config 

def allowed_by_server(uid):
	try:
		global config, ser1, ser2, ser3
		url = config['url_unlock'] + uid
		r = requests.get(url)
		print 'Unlock request:', url
		print 'response status code', r.status_code
		print r.text
		if uid == ser1 or uid == ser2 or uid == ser3: return True
		if r.status_code != 200:
			raise Exception('Server error')
		if (r.text == 'yes'):
			return True
	except:
		lcd_lib.print_lcd('Network error')
		print "Error asking server to unlock: ", sys.exc_info()
		print "Continuing working"
	return False

def allowed_by_list(uid):
	try:
		with open('access_list.txt') as f:
			data = json.load(f, object_hook=date_hook)
		for o in data:
			if (o['uid'] == uid)\
			and (o['date_start'].date() == datetime.date.today())\
			and (o['time_start'].time() <= datetime.datetime.now().time())\
			and (o['time_end'].time() >= datetime.datetime.now().time()):
				return True
	except:
		lcd_lib.print_lcd('Database error')
		print "Error processing access list: ", sys.exc_info()
		update_list()

	return False

def allowed_by_admin(uid):
	try:
		with open('admin_uid.txt', 'rb') as f:
			for line in f:
				if uid == line[:-1]:
					print "Welcome, Admin Adminovich"
					return True
	except:
		lcd_lib.print_lcd('Local error')
		print "Error processing admin list", sys.exc_info()
	return False

def allowed_to_unlock(uid):
	if allowed_by_list(uid) or allowed_by_admin(uid) or allowed_by_server(uid):
		#lcd_lib.print_lcd('Welcome')
		return True
	#lcd_lib.print_lcd('You shall not pass')
	return False

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
		url = config['url_upd']
		r = requests.get(url)
		print 'Update request:', url
		print 'response status code', r.status_code
		if r.status_code != 200:
			raise Exception('Server error')
		json_str = string.replace(r.text, "'", '"')
		with open('access_list.txt', 'w') as f:
			f.write(json_str)
		print "Access list successfully updated"
		data = json.loads(json_str, object_hook=date_hook)
		return data
	except:
		lcd_lib.print_lcd('Network error')
		print "Error asking server to update: ", sys.exc_info()
		print "Continuing working"
	return None

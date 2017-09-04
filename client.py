import requests
import json, string, datetime
import sys

config = {}

def configure(filename):
	try:
		with open(filename) as f:
			data = json.load(f, )
		if (data.get('url_unlock') == None) or (data.get('url_upd') == None) :
			raise Exception('Invalide content of config file')
	except:
		print "Error processing config file: ", sys.exc_info()
		print "Continuing working in an old way"
	else:
		global  config
		config = data
		print "New configuration: ", config 

def allowed_by_server(uid):
	try:
		global config
		url = config['url_unlock'] + uid
		r = requests.get(url)
		print 'Unlock request:', url
		print 'response status code', r.status_code
		print r.text
		if r.status_code != 200:
			raise Exception('Server error')
		if (r.text == 'yes'):
			return True
	except:
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
		print "Error processing access list: ", sys.exc_info()
	return False

def allowed_to_unlock(uid):
	if allowed_by_list(uid) or allowed_by_server(uid):
		return True
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
		print "Error asking server to update: ", sys.exc_info()
		print "Continuing working"
	return None

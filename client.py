import requests
import json, string, datetime
import sys

config = {}

def configure(filename):
	try:
		with open(filename) as f:
			data = json.load(f)
		if (data.get('url_unlock') == None) or (data.get('url_upd') == None) :
			raise Exception('Invalide content of config file')
	except:
		print "Error processing config file: ", sys.exc_info()
		print "Continuing working in an old way"
	else:
		global  config
		config = data
		print "New configuration: ", config 

def allowed_to_unlock(uid):
	try:
		global config
		print config
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


def date_hook(json_dict):
	for (key, value) in json_dict.items():
		try:
			json_dict[key] = datetime.datetime.strptime(value, "datetime.date(%Y, %m, %d)")
		except:
			pass
		try:
			json_dict[key] = datetime.datetime.strptime(value, "datetime.time(%H, %M, %S)")
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
		print json_str
		data = json.loads(json_str, object_hook=date_hook)
		return data
	except:
		print "Error asking server to update: ", sys.exc_info()
		print "Continuing working"
	return None

configure('config.txt')
print allowed_to_unlock('12345')
print update_list()

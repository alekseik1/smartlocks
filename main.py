from client import *

configure('config.txt')
print "alowed tounlock", allowed_to_unlock('12345')
print update_list()
print "allowed to unlock", allowed_to_unlock('12345')
print "allowed to unlock", allowed_to_unlock('1234')

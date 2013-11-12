import urllib
import urllib2

from game.constants import HISCORE_URL


def setWorldTime(levelHash, time):
	post_data_dictionary = {'username':'toto', 'password':'tty', 'scores['+levelHash+']' : time}
	post_data_encoded = urllib.urlencode(post_data_dictionary)
	request_object = urllib2.Request(HISCORE_URL, post_data_encoded)
	res = None
	try:
		response = urllib2.urlopen(request_object)
		res = response.read()
	except:
		pass
	return res if res != 'KO' else None

def getWorldTime(levelHash):
	""" NOTE: returns a string, not an int """
	res = None
	try:
		response = urllib2.urlopen(HISCORE_URL+'/'+levelHash)
		res = response.read()
	except:
		pass
	return res if res != 'KO' else None
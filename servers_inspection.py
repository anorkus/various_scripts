import os
import subprocess


__MOBILE = "0041767098127@mail2sms.sunrise.ch"
__SERVICES_LIST = {
	"McM" : "https://cms-pdmv.cern.ch/mcm/",
	"McM DB" : "https://cms-pdmv.cern.ch/mcm/admin/",
	## fake lucene query
	"McM DB lucene" : "https://cms-pdmv.cern.ch/mcm/admin/users/_fti/_design/lucene/search?q=username:anorkus",
	"McM-dev" : "https://cms-pdmv-dev.cern.ch/mcm/",
	"McM-dev DB" : "https://cms-pdmv-dev.cern.ch/mcm/admin/",
	## fake lucene query 
	"McM-dev DB lucene" : "https://cms-pdmv-dev.cern.ch/mcm/admin/users/_fti/_design/lucene/search?q=username:anorkus",
	#"McM-int" : "https://cms-pdmv-int.cern.ch/mcm/", #????
	"stats" : "https://cms-pdmv-dev.cern.ch/stats/",
	"stats DB" : "https://cms-pdmv-dev.cern.ch/stats/",
	"DQMHisto" : "http://cms-dqm-histo/static/index.html?search_histo_name=true"
}

__PROD_COOKIE = "prod-cookie.txt"
__DEV_COOKIE = "dev-cookie.txt"

def get_cookies(instance_url):
	"""
	method to get cookie file for specific url
	"""
	dev_instance = False
	if "dev" in instance_url:
		dev_instance = True
	if dev_instance:
		cookie_name = __DEV_COOKIE
	else:
		cookie_name = __PROD_COOKIE
	if os.path.exists(cookie_name):
		return True
	else:
		try:
			__args = ["cern-get-sso-cookie", "-u", instance_url, 
					"-o", cookie_name, "--krb"]

			proc = subprocess.Popen(__args, stdout=subprocess.PIPE)
			proc_out = proc.communicate()[0]
		except Exception as ex:
			print "Shit happened while getting cookie. Reason: %s" % (str(ex))
			return False
	return True

def send_sms(msg):
	"""
	sends a message to mobile phone.
	"""

	p1 = subprocess.Popen(["echo", msg], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(["mail", "-s", "serviceInspection",
			__MOBILE],
			stdin=p1.stdout, stdout=subprocess.PIPE)

	output = p2.communicate()[0]
	#print output ##DEBUG

def check_service(name, url):
	"""
	check if curl returns HTTP code 200 -> meaning its fine
	else it should inform via sms that there is error with service
	"""

	## example of curl command to fetch HTTP header response code only
	##curl -k https://cms-pdmv-dev.cern.ch/mcm/admin/ --cookie dev-cookie.txt -I -w "%{http_code}" -o /dev/null

	dev_instance = False
	if "dev" in url:
		dev_instance = True
	if dev_instance:
		cookie_name = __DEV_COOKIE
	else:
		cookie_name = __PROD_COOKIE

	__args = ["curl", "-k", "-s", "--cookie", cookie_name, url, "-I",
			"-w", "%{http_code}", "-o", "/dev/null"]

	proc = subprocess.Popen(__args, stdout=subprocess.PIPE)
	proc_out = proc.communicate()[0]
	print "%s : %s" % (name, proc_out) ##print out for Jenkins

	if proc_out != "200":
		msg = "Error checking %s ERROR code: %s" % (name, proc_out)
		send_sms(msg)




if __name__ == '__main__':
	__success = False
	message = ""
	__success = get_cookies(__SERVICES_LIST["McM"])
	if not __success:
		message = "Error getting -prod cookie"
		print message
		send_sms(message)
	__success = get_cookies(__SERVICES_LIST["McM-dev"])
	if not __success:
		message = "Error getting -dev cookie"
		print message
		send_sms(message)

	for elem in __SERVICES_LIST:
		check_service(elem, __SERVICES_LIST[elem])

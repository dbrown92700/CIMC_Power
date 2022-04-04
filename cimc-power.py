#!/usr/bin/python3

import requests
import base64
import cgi
import cgitb
#import traceback

print('Content-type: text/html\n')

cgitb.enable(display=0, logdir="/tmp")

host = "192.168.1.159"
USER = "admin"
PASSWORD = 'password'

#
# LOGIN
#

basicauth = 'Basic ' + base64.b64encode('{}:{}'.format(USER,PASSWORD).encode('utf-8')).decode('utf-8')
url = "https://{}/nuova".format(host)

payload = "<aaaLogin inName='{}' inPassword='{}' />".format(USER,PASSWORD)
headers = {
  'Authorization': basicauth,
  'Content-Type': 'text/plain'
}

try:
  response = requests.request("POST", url, headers=headers, data = payload, verify=False).text
except:
  print('No response from server')
  exit()

cookie = response[response.find('outCookie')+11:response.find(' outRefresh')-1]

#
# SET POWER
#

#form = cgi.FieldStorage()

try:
  form = cgi.FieldStorage()
  action = form['setpower'].value
except:
  print('No power change requested.<br>')
else:
  payload = """
    <configConfMo cookie='{}' inHierarchical='false'  dn='sys/rack-unit-1' >
      <inConfig>
        <computeRackUnit adminPower='{}' dn='sys/rack-unit-1'>
        </computeRackUnit>
      </inConfig>
    </configConfMo>""".format(cookie,action)
  response = requests.request("POST", url, headers=headers, data = payload, verify=False)

#
# GET POWER STATE
#

payload = """
  <configResolveClass cookie="{}"
  inHierarchical="false" classId="computeRackUnit"/>""".format(cookie)

response = requests.request("POST", url, headers=headers, data = payload, verify=False)

pstate = response.text.find("operPower")
powerstate = response.text[pstate:pstate+15]

#
# WEB PAGE
#

print('Current Power State: {}<br>'.format(powerstate))
print('<a href="http://192.168.1.61/cgi-bin/cimc-power.py?setpower=up">Power On</a><br>')
print('<a href="http://192.168.1.61/cgi-bin/cimc-power.py?setpower=down">Power Off</a><br>')

#
# LOGOUT
#

payload = "<aaaLogout inCookie='{}' />".format(cookie)

response = requests.request("POST", url, headers=headers, data = payload, verify=False).text

# print('<br><xmp>',response,'</xmp><br>')


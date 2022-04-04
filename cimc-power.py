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

basicauth = 'Basic ' + base64.b64encode(f'{USER}:{PASSWORD}'.encode('utf-8')).decode('utf-8')
url = f'https://{host}/nuova'

payload = f"<aaaLogin inName='{USER}' inPassword='{PASSWORD}' />".format(USER,PASSWORD)
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
  payload = f"""
    <configConfMo cookie='{cookie}' inHierarchical='false'  dn='sys/rack-unit-1' >
      <inConfig>
        <computeRackUnit adminPower='{action}' dn='sys/rack-unit-1'>
        </computeRackUnit>
      </inConfig>
    </configConfMo>"""
  response = requests.request("POST", url, headers=headers, data = payload, verify=False)

#
# GET POWER STATE
#

payload = f"""
  <configResolveClass cookie="{cookie}"
  inHierarchical="false" classId="computeRackUnit"/>"""

response = requests.request("POST", url, headers=headers, data = payload, verify=False)

pstate = response.text.find("operPower")
powerstate = response.text[pstate:pstate+15]

#
# WEB PAGE
#

print(f'Current Power State: {powerstate}<br>')
print(f'<a href="/cgi-bin/cimc-power.py?setpower=up">Power On</a><br>')
print(f'<a href="/cgi-bin/cimc-power.py?setpower=down">Power Off</a><br>')

#
# LOGOUT
#

payload = f"<aaaLogout inCookie='{cookie}' />"

response = requests.request("POST", url, headers=headers, data = payload, verify=False).text


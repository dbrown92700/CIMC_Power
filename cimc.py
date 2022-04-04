#!/usr/bin/python3

import requests
import base64
import sys

#
# LOGIN - returns a dictionary item with {'cookie':cookie,'basicauth',basicauth}
#

def login(host, USER, PASSWORD):

  basicauth = 'Basic ' + base64.b64encode('{}:{}'.format(USER,PASSWORD).encode('utf-8')).decode('utf-8')
  url = f"https://{host}/nuova"

  payload = f"<aaaLogin inName='{USER}' inPassword='{PASSWORD}' />"
  headers = {
    'Authorization': basicauth,
    'Content-Type': 'text/plain'
  }

  try:
    response = requests.request("POST", url, headers=headers, data = payload, verify=False).text
  except:
    raise

  cookie = response[response.find('outCookie')+11:response.find(' outRefresh')-1]

  return({'cookie': cookie, 'basicauth': basicauth})


#
# LOGOUT
#

def logout(host, auth):

  url = f"https://{host}/nuova"
  payload = f"<aaaLogout inCookie='{auth['cookie']}' />"
  headers = {
    'Authorization': auth['basicauth'],
    'Content-Type': 'text/plain'
  }

  response = requests.request("POST", url, headers=headers, data = payload, verify=False).text

#
# SET POWER. action = [up,down]
#
def set_power(host, auth, action):

  url = f"https://{host}/nuova"
  payload = f"""
    <configConfMo cookie='{auth['cookie']}' inHierarchical='false'  dn='sys/rack-unit-1' >
      <inConfig>
        <computeRackUnit adminPower='{action}' dn='sys/rack-unit-1'>
        </computeRackUnit>
      </inConfig>
    </configConfMo>"""
  headers = {
    'Authorization': auth['basicauth'],
    'Content-Type': 'text/plain'
  }

  response = requests.request("POST", url, headers=headers, data = payload, verify=False)

  return(response)

#
# GET POWER STATE
#

def get_power(host, auth):

  url = f"https://{host}/nuova"
  payload = f"""
    <configResolveClass cookie="{auth['cookie']}"
    inHierarchical="false" classId="computeRackUnit"/>"""
  headers = {
    'Authorization': auth['basicauth'],
    'Content-Type': 'text/plain'
  }

  response = requests.request("POST", url, headers=headers, data = payload, verify=False)

  pstate = response.text.find("operPower")
  powerstate = response.text[pstate:pstate+15]

  return(powerstate)

if __name__ == '__main__':

  host = "192.168.1.159"
  USER = "admin"
  PASSWORD = 'password'

  try:
    auth = login(host, USER, PASSWORD)
  except:
    print(f'Login failed: {sys.exc_info()[1]}')
  else:
    state = get_power(host, auth)
    print(state)
    logout(host, auth)
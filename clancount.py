#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# run with python3 -O clancount.py to omit debug output

import time
import datetime
from datetime import date, datetime
import requests
from requests_toolbelt.utils import dump
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

#required modules
import logging
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Header for API call, do not change.
api_auth_headers = {
    'X-API-Key': os.getenv('BUNGIE-API-KEY'),
}

#required constants

timestr = time.strftime("%Y%m%d-%H%M%S - ")

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

epoch_time = round(int(time.time()))

# create a custom requests object, modifying the global module throws an error
http = requests.Session()
assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
http.hooks["response"] = [assert_status_hook]

def main():
    print(timestr + "Welcome Guardian")
    
    clanURI = 'https://www.bungie.net/Platform/GroupV2/' + os.getenv('CLAN_ID') + '/'
    
    print (timestr + f"Connecting to Bungie API -- {clanURI}")
    
    clanget = requests.get(clanURI, headers=api_auth_headers)
    
    logging.info(clanget)
    
    if clanget.status_code != 200:
        print (timestr + "There was a problem getting info from the API. Aborting")
        exit()
    
    print (timestr + "Fetching member count...")
    
    APIcount = clanget.json()['Response']['detail']['memberCount']
    
    with open ('clanget.json','r') as infile:
        current_json = json.load(infile)
        
    if current_json['first_run'] == "True":
        print (timestr + "First run detected. Updating local file with current information.")
        current_json.update({"memberCount": APIcount})
        current_json.update({"first_run": "False"})
        with open ('clanget.json','w') as outfile:
            json.dump(current_json,outfile,indent = 4)
        time.sleep(1)
        print (timestr + "First run complete. Exiting.")
        exit()
                        
    current_count = current_json['memberCount']    
    logging.info("Current count: " + str(current_count))
    logging.info("API reports: " + str(APIcount))
    
    if current_count == APIcount:
        print (timestr + "Counts match. Exiting.")
        exit()
    else:
        print (timestr+ "Found a change in counts.")

        if os.getenv('SEND_TO_DISCORD') == 'True':
            ##Build Discord Embed
            discord_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }
            
            uri = os.getenv('DISCORD-WEBHOOK')
            payload = {
                "username": os.getenv('DISCORD_USERNAME'),
                "avatar_url": os.getenv('DISCORD_AVATAR'),
                "content": "",
                "embeds": [
                    {
                        "type": "rich",
                        "title": "Member Count Change",
                        "description": f"\nUpdate as of <t:{epoch_time}:R>\n"
                                       "\n"
                                       f"Current member count is now {APIcount}\n\n",
                        "color": 0x1e1d0e
                    }
                ]
            }
            logging.info(payload)
            response = http.post(uri, headers=discord_headers, json=payload)
            logging.info(response)
        
        print (timestr + "Writing new count to file and exiting.")
        
        current_json.update({"memberCount": APIcount})
            
        with open ('clanget.json','w') as outfile:
            json.dump(current_json,outfile,indent = 4)
        
        exit()
 
if __name__ == "__main__":
    main()

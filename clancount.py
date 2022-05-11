#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 

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

# Workaround for ExceptionError (None variables from .env)
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

# Required modules
import logging
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Header for API call, do not change.
api_auth_headers = {
    'X-API-Key': os.getenv('BUNGIE-API-KEY'),
}

# Required constants

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

epoch_time = round(int(time.time()))

# Do the things

def main():
    logging.info('Welcome Guardian')
    
    clan_URI = 'https://www.bungie.net/Platform/GroupV2/' + os.getenv('CLAN_ID') + '/'
    
    logging.info(f'Connecting to Bungie API -- {clan_URI}')
    
    clan_get = requests.get(clan_URI, headers=api_auth_headers)
    
    logging.debug(clan_get)
    
    if clan_get.status_code != 200:
        logging.error('There was a problem getting info from the API. Aborting')
        exit()
    
    logging.info('Fetching member count...')
    
    api_count = clan_get.json()['Response']['detail']['memberCount']
    
    with open ('clan_get.json','r') as infile:
        current_json = json.load(infile)
        
    if current_json['first_run'] == "True":
        logging.info('First run detected. Updating local file with current information.')
        current_json.update({"memberCount": api_count})
        current_json.update({"first_run": "False"})
        with open ('clan_get.json','w') as outfile:
            json.dump(current_json,outfile,indent = 4)
        time.sleep(1)
        logging.info('First run complete. Exiting.')
        exit()
                        
    current_count = current_json['memberCount']    
    logging.info(f'Current count: {current_count}')
    logging.info(f'API reports: {api_count}')
    
    if current_count == api_count:
        logging.info('Counts match. Exiting.')
        exit()
    else:
        logging.info('Found a change in counts.')

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
                                       f"Current member count is now {api_count}\n\n",
                        "color": 0x1e1d0e
                    }
                ]
            }
            logging.debug(payload)
            response = http.post(uri, headers=discord_headers, json=payload)
            logging.debug(response)
        
        logging.info('Writing new count to file and exiting.')
        
        current_json.update({"memberCount": api_count})
            
        with open ('clan_get.json','w') as outfile:
            json.dump(current_json,outfile,indent = 4)
        
        exit()
 
if __name__ == "__main__":
    main()

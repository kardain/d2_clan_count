#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 

import time
import requests
import os
import json
from pathlib import Path
from dotenv import load_dotenv

#Workaround for None type when calling from .env

script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

#required modules

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.os.getenv('LOGGING_LEVEL'),
    datefmt='%Y-%m-%d %H:%M:%S')

# Header for API call, do not change.
api_auth_headers = {'X-API-Key': os.getenv('BUNGIE-API-KEY')}

###

def main():
    logging.info(os.getenv('WELCOME-TEXT'))
    
    clanURI = 'https://www.bungie.net/Platform/GroupV2/' + os.getenv('CLAN_ID')
    
    logging.info(f"{os.getenv('CONNECTING')} -- {clanURI}")
    
    clanget = requests.get(clanURI, headers=api_auth_headers)
    
    logging.debug(clanget)
    
    if clanget.status_code != 200:
        logging.error(os.getenv('ERROR'))
        exit()
    
    logging.info(os.getenv('FETCHING'))
    
    APIcount = clanget.json()['Response']['detail']['memberCount']
    
    with open ('clanget.json','r') as infile:
        current_json = json.load(infile)
        
    if current_json['first_run'] == "True":
        logging.info(os.getenv('FIRST-RUN-TRUE'))
        current_json.update({"memberCount": APIcount})
        current_json.update({"first_run": "False"})
        with open ('clanget.json','w') as outfile:
            json.dump(current_json,outfile,indent = 4)
        time.sleep(1)
        logging.info(os.getenv('FIRST-RUN-COMPLETE'))
        exit()
                        
    current_count = current_json['memberCount']    
    logging.info(f"Current count: {current_count}")
    logging.info(f"API reports: {APIcount}")
    
    if current_count == APIcount:
        logging.info(os.getenv('COUNT-MATCHES'))
        exit()
    else:
        logging.info(os.getenv('COUNT-CHANGE'))

        if os.getenv('SEND_TO_DISCORD') == 'True':
            ##Build Discord Embed
            discord_headers = {'Content-Type': 'application/json','Accept': 'application/json'}            
            uri = os.getenv('DISCORD-WEBHOOK')
            payload = {
                "username": os.getenv('DISCORD_USERNAME'),
                "avatar_url": os.getenv('DISCORD_AVATAR'),
                "content": "\u200c",
                "embeds": [
                    {
                        "type": "rich",
                        "title": os.getenv('DISCORD_TITLE'),
                        "description": f"\n{os.getenv('DISCORD_DESC_1')} <t:{round(int(time.time()))}:R>\n"
                                       "\n"
                                       f"{os.getenv('DISCORD_DESC_2')} {APIcount}\n\n",
                        "color": int(os.getenv('DISCORD_COLOR'))#0x1e1d0e
                    }
                ]
            }
            logging.info(payload)
            response = requests.post(uri, headers=discord_headers, json=payload)
            logging.info(response)
        
        logging.info(os.getenv('LOCAL-FILE-UPDATE'))
        
        current_json.update({"memberCount": APIcount})
            
        with open ('clanget.json','w') as outfile:
            json.dump(current_json,outfile,indent = 4)
        
        exit()
 
if __name__ == "__main__":
    main()


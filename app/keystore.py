import configparser
import os
from . import request_api as req
import FreeSimpleGUI as sg

cfg_path='app/assets/keys/settings.cfg'

def handle_keystore(login_window, current_image):
    imagepath = current_image['-IMAGE-']
    api_choice = req.get_api_choice(imagepath)
    cfg_key = req.get_cfg_key(imagepath)
    new_api_key = load_api_key(api_choice, cfg_key)
    login_window['-API-'].update(value=new_api_key)
    sg.popup_auto_close(f'Pasted the API Key for {api_choice}', auto_close_duration=2)

def save_api_key(identifier, api_key, key_name, cfg_path=cfg_path):
    
    config = configparser.ConfigParser()
    if not api_key.strip():
        return
    # Load existing config if it exists
    if os.path.exists(cfg_path):
        config.read(cfg_path)

    if not config.has_section("Main"):
        config.add_section("Main")
    if not config.has_section(identifier):
        config.add_section(identifier)

    config.set("Main", "RecentAPI", api_key)  # Previously used API key
    config.set(identifier, key_name, api_key) # Current used API key

    # Save to file (overwrites content, but config holds all existing values)
    with open(cfg_path, 'w') as configfile:
        config.write(configfile)

    print(f"API key saved to '{cfg_path}' under section [{identifier}].")
    print(cfg_path)

def load_api_key(identifier, key_name, cfg_path=cfg_path):
    config = configparser.ConfigParser()
    if not os.path.exists(cfg_path):
        print(f"No config file found at {cfg_path}. Please save an API key first.")
        return None

    config.read(cfg_path)
    # Use the identifier passed in directly, do NOT override it
    if config.has_section(identifier) and config.has_option(identifier, key_name):
        return config.get(identifier, key_name)
    else:
        print(f"No API key found in section [{identifier}] under key '{key_name}'.")
        return None

def load_git_token(cfg_path=cfg_path):
    config = configparser.ConfigParser()
    if not os.path.exists(cfg_path):
        print(f"No config file found at {cfg_path}. Please save an API key first.")
        return None
    
    config.read(cfg_path)
    if config.has_section('GitHub') and config.has_option('GitHub', 'GITHUB_TOKEN'):
        return config.get('GitHub', 'GITHUB_TOKEN')
    else:
        print(f"No API key found in section [{'GitHub'}] under key '{'GITHUB_TOKEN'}'.")
        return None
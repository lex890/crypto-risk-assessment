import configparser
import os
from . import request_api as req
import FreeSimpleGUI as sg

cfg_path = 'app/assets/keys/settings.cfg'

def handle_keystore(login_window):
    imagepath = 'app/assets/images/CMC.png' if login_window['-CRYPTO-NAME-TOGGLE-'].get() == 'CoinMarketCap' else 'app/assets/images/CG.png'
    api_choice = req.get_api_choice(imagepath)
    cfg_key = get_cfg_key(imagepath)
    api_keys = load_api_key(api_choice, cfg_key)
    login_window['-API-'].update(value=api_keys[0] if api_keys else '')  # Display the first key if available
    sg.popup_auto_close(f'Pasted the API Key for {api_choice}', auto_close_duration=2)

def get_cfg_key(imagepath):
    cfg_key = 'CMCKEY' if imagepath == 'app/assets/images/CMC.png' else 'CGKEY'
    return cfg_key

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

    # Get existing keys or initialize an empty list
    existing_keys = []
    if config.has_option(identifier, key_name):
        existing_keys = config.get(identifier, key_name).split(',')
        existing_keys = [key.strip() for key in existing_keys if key.strip()]  # Clean up any empty strings

    # Add new key if it's not already in the list
    if api_key not in existing_keys:
        existing_keys.append(api_key)

    # Save the keys as a comma-separated string
    config.set("Main", "RecentAPI", api_key)  # Store the most recent API key
    config.set(identifier, key_name, ','.join(existing_keys))  # Store all keys as a comma-separated string

    # Save to file
    with open(cfg_path, 'w') as configfile:
        config.write(configfile)

    print(f"API key saved to '{cfg_path}' under section [{identifier}].")
    print(cfg_path)

def load_api_key(identifier='CoinMarketCap', key_name='CMCKEY', cfg_path=cfg_path):
    config = configparser.ConfigParser()
    if not os.path.exists(cfg_path):
        print(f"No config file found at {cfg_path}. Please save an API key first.")
        return []

    config.read(cfg_path)
    if config.has_section(identifier) and config.has_option(identifier, key_name):
        keys = config.get(identifier, key_name).split(',')
        keys = [key.strip() for key in keys if key.strip()]  # Clean up and filter empty strings
        return keys
    else:
        print(f"No API key found in section [{identifier}] under key '{key_name}'.")
        return []

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
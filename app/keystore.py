import configparser
import os

cfg_path='./keys/settings.cfg'

# Your functions here...
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


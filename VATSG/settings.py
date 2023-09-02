import win32cred
import json
import win32timezone
import platform
import os

# API 키 저장

def save_apikey(apikey):
    cred_info = {
        'Type': win32cred.CRED_TYPE_GENERIC,
        'TargetName': 'VATSG',
        'CredentialBlob': apikey,
        'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE
    }
    win32cred.CredWrite(cred_info)
def load_apikey():
    try:
        cred_info = win32cred.CredRead(Type=win32cred.CRED_TYPE_GENERIC, TargetName='VATSG')
        api_key = cred_info['CredentialBlob']
        return api_key
    except Exception as e:
        print("API Key not found. Error:", e)

def get_settings_path():
    if platform.system() == 'Windows':
        return os.path.join(os.environ['APPDATA'], 'VATSG', 'settings.json')
    elif platform.system() == 'Darwin':  # macOS
        return os.path.join(os.path.expanduser('~/Library/Application Support/VATSG'), 'settings.json')
    else:  # Linux and others
        return os.path.join(os.path.expanduser('~/.config/VATSG'), 'settings.json')

def settingjson(uiwrapper):
    settings_path = get_settings_path()

    settings_dir = os.path.dirname(settings_path)
    if not os.path.exists(settings_dir):
        os.makedirs(settings_dir)

    settings = {"cuda_var": uiwrapper.get_cuda_var(), "translateoption_var": uiwrapper.get_translateoption_Var(),
                "sourcelanguagecodeinput": uiwrapper.get_srclanguagecodeinput(),
                "targetlanguagecodeinput": uiwrapper.get_trglanguagecodeinput(), "original": uiwrapper.get_original_var(), "fast": uiwrapper.get_fast_var()}
    with open(get_settings_path(), "w", encoding="utf8") as f:
        json.dump(settings, f)


def load_settings():
    try:
        with open(get_settings_path(), "r") as f:
            settings = json.load(f)
            return settings
    except FileNotFoundError:
        return None, {}
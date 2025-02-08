import requests
import os.path
import tkinter
from tkinter import filedialog
from zipfile import ZipFile

from KnowPyEnemy import KpyEconfig

def download_github_asset(repo, asset_name, destination):
    response = requests.get("https://api.github.com/repos/" + repo + "/releases/latest")

    if not os.path.isfile(asset_name):
        try:
            # Getting the release asset
            asset = [asset for asset in response.json().get('assets') if asset.get('name') == asset_name][-1]
            ## Getting asset binary content
            asset_binary = requests.get(asset.get('url'), headers={'Accept': 'application/octet-stream'})

            if asset_binary.status_code == 200:
                with open(os.path.join(destination, asset_name), 'wb') as f:
                    f.write(asset_binary.content)
        except:
            #TODO: get status code(s) and explain error
            raise Exception("There has been en error downloading " + asset_name)
    else:
        print(asset_name + " is already present, no need to download it...")

def extract_zip(zipfile, destination,):
    with ZipFile(zipfile, 'r') as zObject:
        zObject.extractall(
            path=os.path.join(destination, zipfile.split('.')[0])
        )

def set_arcdps_log_directory():
    tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
    return filedialog.askdirectory(title="Select directory to your ARCDPS logs")

def adjust_GW2EICLI_settings():
    settingsfile = r"GW2EICLI\Settings\sample.conf"
    tmp = []
    with open(settingsfile, 'r') as f:
        for line in f.readlines():
            if any(x in line for x in ['DetailledWvW', 'SaveOutJSON', 'IndentJSON']):
                tmp.append(line.removeprefix('#').replace('false', 'true'))
            elif any(x in line for x in ['SaveOutHTML']):
                tmp.append(line.removeprefix('#').replace('true', 'false'))
            else:
                tmp.append(line)
    with open(settingsfile, 'w') as f:
        f.writelines(tmp)

if __name__ == "__main__":

    # welcome
    print("\nKnowPyEnemy Setup Script\n")

    # download & extract GW2 Elite Insights Parser CLI
    repo = "baaron4/GW2-Elite-Insights-Parser"
    asset_name = 'GW2EICLI.zip'
    download_github_asset(repo, asset_name, '.')
    extract_zip(asset_name,'.')

    # adapt converter settings for our needs
    adjust_GW2EICLI_settings()

    # setup own config file and ask user for the ARCDPS log location
    setupKpyE = KpyEconfig()
    setupKpyE.generate_config(set_arcdps_log_directory())
    setupKpyE.write_config()
    setupKpyE.read_config()

    # printout current setup
    GW2EICLI = os.path.join('GW2EICLI', 'GuildWars2EliteInsights-CLI.exe')
    if os.path.isfile(GW2EICLI):
        print("Current config:")
        [print('  ' + key + '=' + str(val)) for key, val in setupKpyE.__dict__.items()]
        print("\nSetup finished")







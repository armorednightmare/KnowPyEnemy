import os
import glob
import subprocess
import json
import colorama
import math
from colorama import Fore, Style, init
from tabulate import tabulate
from collections import Counter, OrderedDict

colorama.init()

class KpyEconfig():
    def __init__(self):
        self.ARCDPS_LOG_LOCATION = ''
        self.GW2EICLI_LOCATION = 'GW2EICLI'
        self.GENERATE_KPYE_FILES = True
        self.KEEP_JSON = False
        self.KEEP_CI_LOG = False

    def __iter__(self):
        return self.__dict__.items()

    def consistancy_checks(self):
        if not os.path.isdir(self.ARCDPS_LOG_LOCATION):
            raise Exception("ARCDPS_LOG_LOCATION is not a directory!")
        if not os.path.isdir(self.GW2EICLI_LOCATION):
            raise Exception("GW2EICLI_LOCATION is not a directory!")
        if not type(self.GENERATE_KPYE_FILES) == bool:
            raise Exception("GENERATE_KPYE_FILES is not of boolean type!")

    def generate_config(self, arcdps_location):
        self.ARCDPS_LOG_LOCATION = arcdps_location
        self.consistancy_checks()

    def write_config(self):
        with open('KnowPyEnemy.conf', 'w') as f:
            f.writelines([key + '=' + str(val) + '\n' for key, val in self.__dict__.items()])
        self.consistancy_checks()

    def read_config(self):
        with open('KnowPyEnemy.conf', 'r') as f:
            for line in f.readlines():
                line=line.removesuffix('\n')
                conf = line.split('=')
                conf[1] = conf[1].lower() in ("true", True) if conf[1].lower() in ("true", "false") else conf[1]
                setattr(self,conf[0],conf[1])
        self.consistancy_checks()
        return self

    def show_config(self, print_conf=False):
        output = []
        [output.append('  ' + key + '=' + str(val)) for key, val in self.__dict__.items()]
        if print_conf:
            print("Current config:")
            [print(line) for line in output]
        return output

def find_zevtc_files(folder: str, simple_text_filter: str):
    files_path = os.path.join(folder, '**/*.zevtc')
    files = sorted(
        glob.iglob(files_path, recursive=True), key=os.path.getctime, reverse=True)
    files = [file for file in files if simple_text_filter in str(file)]
    return files

def convert_zevtc_to_json(gw2eicli_loc, zevtc_file: str):
    exe = r'GuildWars2EliteInsights-CLI.exe'
    config = os.path.join(gw2eicli_loc, r'Settings\sample.conf')
    call_str = ' '.join([os.path.join(gw2eicli_loc, exe), '-c' , '\"' + config + '\"', '\"' + zevtc_file + '\"'])

    # convert zevtc to json, suppressed output
    retcode = subprocess.call(call_str,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)

    json_file = glob.glob(zevtc_file.replace(".zevtc", "*.json"))

    if len(json_file)==0 or retcode !=0 :
        raise Exception("There has been an error with the CLI converter")

    return json_file[0]

def team_id2color(team_id):
    if team_id == 707:
        return ["Red", Fore.RED]
    if team_id == 2767:
        return ["Green", Fore.GREEN]
    if team_id == 433:
        return ["Blue", Fore.BLUE]
    return [str(team_id), Fore.RESET]

def extract_player_count(json_file: str):
    randoms = 0

    with open(json_file) as f:
        d = json.load(f)
        f.flush()

    allies = d.get('players')
    squad = [player for player in allies if player.get('group') <= 50 ]
    randoms = [player for player in allies if player.get('group') > 50]

    #enemies = [target for target in targets if target.get('enemyPlayer') == True ]
    target_team_ids = list(set([target.get('teamID') for target in d.get('targets')]))
    target_team_ids.remove(0) # remove dummy PvP agent
    enemies = dict()
    classes = dict()
    lines = dict()
    class_str = ''
    for count, team in enumerate(target_team_ids):
        enemies[team] = [target for target in d.get('targets') if target.get('teamID') == target_team_ids[count] and target.get('enemyPlayer') == True]
        classes[team] = Counter([target.get('name').split(' ')[0] for target in d.get('targets') if target.get('teamID') == target_team_ids[count] and target.get('enemyPlayer') == True])
        classes[team] = OrderedDict(classes[team].most_common())
        num_col = math.ceil(len(classes[team]) / 5)
        num_lin = 5 if len(classes[team])>=5 else len(classes[team])

        lines[team] = []
        header = []

        for l in range(num_lin):
            line_tmp = []
            for c in range(num_col):
                #header.extend(['Class', 'Count'])
                try:
                    line_tmp.extend([[cnt, cls] for cls, cnt in classes[team].items()][5 * c + l])
                except:
                    None
            lines[team].append(line_tmp)

        lines[team] = (tabulate(lines[team], headers = header, numalign="left"))
        class_str +=  team_id2color(team)[1] + '\nTeam ' + team_id2color(team)[0] + ' (' + str(len(enemies[team])) + '): \n' + Style.RESET_ALL + str(lines[team]) + "\n" + Fore.RESET

    team_cnt = tuple([len(enemies[team]) for team in enemies])
    teams_str = ' ' + str(team_cnt).replace(',', " +") if len(team_cnt)>1 else ''

    result = str(
        Style.BRIGHT +
        Fore.LIGHTRED_EX + str(sum(team_cnt)) + ' Enemies' + Fore.RESET + teams_str +
        Fore.RESET + ' vs. ' +
        Fore.LIGHTGREEN_EX + str(len(allies)) + ' Allies' +
        Fore.RESET +' (' + str(len(squad)) + ' in Squad + ' + str(len(randoms)) + ' Randoms)' +
        Style.RESET_ALL)

    return [result, class_str]

def process_zevtc_files(KpyEconf: KpyEconfig, zevtc_files: list):

    output = []

    for count, zevtc_file in enumerate(zevtc_files):

        output = []
        zevtc_filename = os.path.splitext(os.path.basename(zevtc_file))[0]

        # check if a KpyE file exists, if so, take these results, skip conversion etc
        KpyE_file = glob.glob(os.path.join(os.path.dirname(zevtc_file), zevtc_filename + '*.KpyE'))

        # show current progress counter
        print('(' + str(count + 1) + '/' + str(len(zevtc_files)) + ') ', end='')

        if len(KpyE_file) == 1:
            KpyE_file = KpyE_file[0]
            if os.path.isfile(KpyE_file):  # redundant
                # read back file to show results
                print("read from " + KpyE_file)
                with open(KpyE_file, 'r') as fin:
                    result = fin.read()
                    for line in result.split('\n'):
                        output.append(line)
                    fin.flush()
        else:
            processing = True

            # print file name
            output.append(zevtc_file + ': ')

            # check if a json file exists, if so, extract the player counts and skip conversion
            json_file = glob.glob(os.path.join(os.path.dirname(zevtc_file), zevtc_filename + '*.json'))
            if len(json_file) == 1:
                json_file = json_file[0]
                if os.path.getsize(json_file) == 0:
                    # faulty/empty json file, we should not process it
                    processing = False
                output.append(json_file)
            else:
                # no associated file found, start processing
                json_file = convert_zevtc_to_json(KpyEconf.GW2EICLI_LOCATION, zevtc_file)
            if processing:
                try:
                    data = extract_player_count(json_file)
                    result = data[0]
                    detail = data[1]
                except:
                    print("WARNING: an error occurred while processing " + json_file)
                    continue

                # write data to output
                output.append('\n         ' + result)
                for line in detail.split('\n'):
                    output.append('         ' + line)

                # write data to a KpyE file
                if KpyEconf.GENERATE_KPYE_FILES:
                    KpyE_file = json_file.replace("json", "KpyE")
                    with open(KpyE_file, "a") as f:
                        for line in output:
                            f.write(line + '\n')
                        f.flush()

            # some cleanup (json files use quite some space)
            if not KpyEconf.KEEP_JSON:
                if os.path.isfile(json_file):
                    os.remove(json_file)
            if not KpyEconf.KEEP_CI_LOG:
                log_file = zevtc_file.replace("zevtc", "log")
                if os.path.isfile(log_file):
                    os.remove(log_file)

        # we have done some work, show that
        output.append(" ")  # newline
        for line in output:
            print(line)

    return output

if __name__ == "__main__":

    KpyEconf = KpyEconfig()
    KpyEconf.read_config()



    # the script will process all found files, beginning from the latest date modified, limit the number here
    latest_x_files = 20

    zevtc_files = find_zevtc_files(KpyEconf.ARCDPS_LOG_LOCATION, 'WvW')[:latest_x_files]
    res = process_zevtc_files(KpyEconf, zevtc_files)

    input('Press ENTER to exit')




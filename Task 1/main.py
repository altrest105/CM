import zipfile

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ShellEmulator:
    def __init__(self, username, zip_path):
        self.username = username
        self.zip_path = zip_path
        self.current_dir = ""

    def command_ls(self):
       with zipfile.ZipFile(self.zip_path, 'r') as zip:
           all_files = zip.namelist()
           files = {item.split('/')[0] for item in all_files if item.startswith(self.current_dir)}
           for item in files:
               print(f"{bcolors.OKCYAN}{item}{bcolors.OKCYAN}")
           return 0

shell = ShellEmulator("root", "test.zip")
shell.command_ls()
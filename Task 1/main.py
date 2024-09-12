import zipfile

class ShellEmulator:
    #Конструктор
    def __init__(self, username, zip_path):
        self.username = username
        self.zip_path = zip_path
        self.current_dir = ""

    #Получение цвета по расширению файла
    def get_color_for_extension(self, extension):
        extension_colors = {
            '.txt': '\033[94m', #OKBLUE
            '.py': '\033[92m', #OKGREEN
            '.jpg': '\033[93m', #WARNING
            '.png': '\033[93m', #WARNING
            '.zip': '\033[91m', #FAIL
            '.exe': '\033[96m', #OKCYAN
            '': '\033[1m', #BOLD
        }
        return extension_colors.get(extension, '\033[0m')

    #Команда ls
    def command_ls(self):
        with zipfile.ZipFile(self.zip_path, 'r') as zip:
            all_files = zip.namelist()
            files = {item.split('/')[0] for item in all_files if item.startswith(self.current_dir)}
            for item in sorted(files, reverse = True):
                file_extension = '.' + item.split('.')[-1] if '.' in item else ''
                color = self.get_color_for_extension(file_extension)
                print(f"{color}{item}\033[0m")
            return 0

shell = ShellEmulator("root", "test.zip")
shell.command_ls()
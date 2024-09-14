import zipfile
import sys

extensions = ['txt', 'py', 'jpg', 'png', 'zip', 'exe']

class ShellEmulator:
    # Конструктор
    def __init__(self, username, zip_path):
        self.username = username
        self.zip_path = zip_path
        self.current_dir = ''
        self.all_files = (zipfile.ZipFile(zip_path, 'r')).namelist()
        self.file_owners = {file: 'root' for file in self.all_files}
        if username == 'root':
            self.root = '#'
        else:
            self.root = '$'

    # Получение цвета по расширению файла
    def get_color_for_extension(self, extension):
        extension_colors = {
            '.txt': '\033[94m', # OKBLUE
            '.py': '\033[92m', # OKGREEN
            '.jpg': '\033[93m', # WARNING
            '.png': '\033[93m', # WARNING
            '.zip': '\033[91m', # FAIL
            '.exe': '\033[96m', # OKCYAN
            '.pdf': '\033[95m', # HEADER
            '.docx': '\033[95m', # HEADER
            '': '\033[1m', # BOLD
        }
        return extension_colors.get(extension, '\033[0m')

    # Команда ls
    def command_ls(self):
        files = {item.replace(self.current_dir, '', 1).split('/')[0] for item in self.all_files if item.startswith(self.current_dir)}

        for item in sorted(files, reverse = True):
            file_extension = '.' + item.split('.')[-1] if '.' in item else ''
            color = self.get_color_for_extension(file_extension)
            print(f'{color}{item}\033[0m')

    # Команда cd
    def command_cd(self, path=''):
        # Если нет аргументов, переходим в домашнюю директорию
        if path == '':
            self.current_dir = ''
            return

        # Определяем целевой путь
        if (path.startswith('/')) and (f'{path[1:]}/' in self.all_files) and (path.split('.')[-1] not in extensions): # Абсолютный путь с / в начале
            target_dir = f'{path[1:]}/'
            self.current_dir = target_dir
        elif (path.split('.')[-1] not in extensions) and ('/' not in path) and (f'{self.current_dir}{path}/' in self.all_files): # Перейти в папку в текущей директории
            target_dir = f'{self.current_dir}{path}/'
            self.current_dir = target_dir
        else:
            print(f'Ошибка: {path} не является директорией')

    # Команда pwd
    def command_pwd(self):
        print(f'/{self.current_dir[:-1]}' if self.current_dir else f'/{self.username}')

    #Команда chown
    def command_chown(self, new_owner, path):
        abs_path = f'{self.current_dir}{path}/' if not path.startswith('/') else f'{path[1:]}/'

        if abs_path in self.file_owners:
            self.file_owners[abs_path] = new_owner
            print(f'Владелец {abs_path[:-1]} сменён на {new_owner}')
        else:
            print(f'Ошибка: {path} не существует')



# Проверяем, что переданы аргументы
if len(sys.argv) != 3:
    print('Использование: py <название_программы.py> <имя_пользователя> <путь_к_архиву.zip>')
    sys.exit(1)

username = sys.argv[1]
zip_path = sys.argv[2]
shell = ShellEmulator(username, zip_path)

# Ввод команд
while True:
    command = input(f'{shell.username}@localhost:~/{shell.current_dir}{shell.root} ').split()
    if not command:
        continue  # Пустая строка
    cmd_name = command[0]
        
    if cmd_name == 'ls':
        shell.command_ls()

    elif cmd_name == 'cd':
        if len(command) == 1:
            shell.command_cd()
        else:
            shell.command_cd(' '.join(command[1:]).rstrip())

    elif cmd_name == 'pwd':
        shell.command_pwd()

    elif cmd_name == 'exit':
        exit()

    elif cmd_name == 'chown':
        if len(command) == 3:
            shell.command_chown(command[1], command[2])
        else:
            print('Использование: chown <новый_владелец> <файл>')

    else:
        print('Неизвестная команда, попробуйте снова!')
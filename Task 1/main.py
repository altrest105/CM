import zipfile
import sys

class ShellEmulator:
    # Конструктор
    def __init__(self, username, zip_path):
        self.username = username
        self.zip_path = zip_path
        self.archive = zipfile.ZipFile(zip_path, 'r')
        self.current_dir = ''
        self.all_files = self.archive.namelist()
        self.file_owners = {file: 'root' for file in self.all_files}
        if username == 'root':
            self.root = '#'
        else:
            self.root = '$'

    # Получение цвета по расширению файла
    def get_color_for_extension(self, extension):
        extension_colors = {
            'txt': '\033[94m', # OKBLUE
            'py': '\033[92m', # OKGREEN
            'jpg': '\033[93m', # WARNING
            'png': '\033[93m', # WARNING
            'zip': '\033[91m', # FAIL
            'exe': '\033[96m', # OKCYAN
            'pdf': '\033[95m', # HEADER
            'docx': '\033[95m', # HEADER
            '': '\033[1m', # BOLD
        }
        return extension_colors.get(extension, '\033[0m')

    # Команда ls
    def command_ls(self):
        files = {item.replace(self.current_dir, '', 1).split('/')[0] for item in self.all_files if item.startswith(self.current_dir)}

        for item in sorted(files, reverse = True):
            file_extension = item.split('.')[-1] if '.' in item else ''
            color = self.get_color_for_extension(file_extension)
            own = self.file_owners.get(f'{self.current_dir}{item}')
            owner = own if own is not None else self.file_owners.get(f'{self.current_dir}{item}/')
            if item != '':
                print(f'{color}{item}\033[0m (owner: {owner})')

    # Команда cd
    def command_cd(self, path=''):
        # Если нет аргументов, переходим в домашнюю директорию
        if path == '':
            self.current_dir = ''
            return
        
        abs_path = f'{self.current_dir}{path}/' if not path.startswith('/') else f'{path[1:]}/'
        # Определяем целевой путь
        if abs_path in self.all_files:
            self.current_dir = abs_path
        else:
            print(f'Ошибка: Неправильный путь {path}')

    # Команда pwd
    def command_pwd(self):
        print(f'/{self.current_dir[:-1]}' if self.current_dir else f'/{self.username}')

    #Команда chown
    def command_chown(self, new_owner, path):
        abs_path = f'{self.current_dir}{path}/' if not path.startswith('/') else f'{path[1:]}/'

        if abs_path in self.file_owners:
            self.file_owners[abs_path] = new_owner
            print(f'Владелец {abs_path[:-1]} сменён на {new_owner}')
        elif abs_path[:-1] in self.file_owners:
            self.file_owners[abs_path[:-1]] = new_owner
            print(f'Владелец {abs_path[:-1]} сменён на {new_owner}')
        else:
            print(f'Ошибка: Неправильный путь {path}')

    #Команда uniq
    def command_uniq(self, path):
        abs_path = f'{self.current_dir}{path}' if not path.startswith('/') else f'{path[1:]}'

        if (abs_path in self.all_files) and (abs_path.split('.')[-1] == 'txt'):
            with self.archive.open(abs_path) as file:
                lines = file.readlines()
                unique_lines = []
                previous_line = None

                for line in lines:
                    if line != previous_line:
                        unique_lines.append(line)
                        previous_line = line

                for unique_line in unique_lines:
                    print(unique_line.decode('utf8').strip())
        else:
            print(f'Ошибка: Неправильный путь {path}')

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
        if len(command) == 1:
            shell.command_ls()
        else:
            print('Использование: ls')

    elif cmd_name == 'cd':
        if len(command) == 1:
            shell.command_cd()
        elif len(command) == 2:
            shell.command_cd(' '.join(command[1:]).rstrip())
        else:
            print('Использование: cd <папка_назначения>')

    elif cmd_name == 'pwd':
        if len(command) == 1:
            shell.command_pwd()
        else:
            print('Использование: pwd')

    elif cmd_name == 'exit':
        if len(command) == 1:
            exit()
        else:
            print('Использование: exit')

    elif cmd_name == 'chown':
        if len(command) == 3:
            shell.command_chown(command[1], command[2])
        else:
            print('Использование: chown <новый_владелец> <файл>')

    elif cmd_name == 'uniq':
        if len(command) == 2:
            shell.command_uniq(command[1])
        else:
            print('Использование: uniq <файл>')

    else:
        print('Неизвестная команда, попробуйте снова!')
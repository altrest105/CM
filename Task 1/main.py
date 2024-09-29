import zipfile
import sys
import tkinter as tk


class ShellEmulator:
    # Конструктор
    def __init__(self, username, zip_path):
        self.username = username
        self.zip_path = zip_path
        with zipfile.ZipFile(self.zip_path, 'r') as zip_file:
            self.archive = zip_file
            self.all_files = zip_file.namelist()
        self.archive = zipfile.ZipFile(zip_path, 'r') # Необходимо повторное открытие для uniq
        self.current_dir = ''
        self.file_owners = {file: 'root' for file in self.all_files}
        if username == 'root':
            self.root = '#'
        else:
            self.root = '$'

    # Получение цвета по расширению файла
    def get_color_for_extension(self, extension):
        extension_colors = {
            'txt': 'OKBLUE',
            'py': 'OKGREEN',
            'jpg': 'WARNING',
            'png': 'WARNING',
            'zip': 'FAIL',
            'exe': 'OKCYAN',
            'pdf': 'HEADER',
            'docx': 'HEADER',
            '': 'BOLD',
        }
        return extension_colors.get(extension, None)

    # Команда ls
    def command_ls(self):
        res = []
        files = {item.replace(self.current_dir, '', 1).split('/')[0] for item in self.all_files if item.startswith(self.current_dir)}

        for item in sorted(files, reverse = True):
            file_extension = item.split('.')[-1] if '.' in item else ''
            color = self.get_color_for_extension(file_extension)
            own = self.file_owners.get(f'{self.current_dir}{item}')
            owner = own if own is not None else self.file_owners.get(f'{self.current_dir}{item}/')
            if item != '':
                res.append([f'{item} (owner: {owner})\n', color])
        return res

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
            return(f'Ошибка: Неправильный путь {path}\n')

    # Команда pwd
    def command_pwd(self):
        return(f'/{self.current_dir[:-1]}' if self.current_dir else f'/{self.username}')

    #Команда chown
    def command_chown(self, new_owner, path):
        abs_path = f'{self.current_dir}{path}/' if not path.startswith('/') else f'{path[1:]}/'

        if abs_path in self.file_owners:
            self.file_owners[abs_path] = new_owner
        elif abs_path[:-1] in self.file_owners:
            self.file_owners[abs_path[:-1]] = new_owner
        else:
            return(f'Ошибка: Неправильный путь {path}\n')

    #Команда uniq
    def command_uniq(self, path):
        res = []
        abs_path = f'{self.current_dir}{path}' if not path.startswith('/') else f'{path[1:]}'

        if (abs_path in self.all_files) and (abs_path.split('.')[-1] == 'txt'):
            with self.archive.open(abs_path) as file:
                previous_line = None

                for line in file:
                    if line != previous_line:
                        res.append(line.decode('utf8'))
                        previous_line = line
            return res
        else:
            return(f'Ошибка: Неправильный путь {path}\n')


class Application(tk.Tk):
    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        self.title('Shell Emulator')

        self.console = tk.Text(self, wrap='word', bg='black', fg='white', height=20, width=80, font=("Consolas", 12))
        self.console.pack(expand=True, fill='both')
        self.user()

        self.console.tag_configure("OKBLUE", foreground="#0000ff")
        self.console.tag_configure("OKGREEN", foreground="#00ff00")
        self.console.tag_configure("WARNING", foreground="#ffcc00")
        self.console.tag_configure("FAIL", foreground="#ff0000")
        self.console.tag_configure("OKCYAN", foreground="#00ffff")
        self.console.tag_configure("HEADER", foreground="#ff66ff")
        self.console.tag_configure("BOLD", font=("Consolas", 12, "bold"))

        self.console.bind('<Return>', self.execute_command)
        self.console.mark_set('insert', 'end')

    def execute_command(self, event):
        cursor_position = self.console.index(tk.INSERT)
        command_line = self.console.get('insert linestart', cursor_position).strip()
        command = command_line.split()[1:]

        if not command:
            self.console.insert(tk.END, '\n')
            self.console.see(tk.END)
            self.console.mark_set('insert', 'end')
            self.user()
            return 'break'
        
        cmd_name = command[0]
        result = ''

        if cmd_name == 'ls':
            if len(command) == 1:
                self.console.insert(tk.END, '\n')
                result = self.shell.command_ls()
                for item in result:
                    self.console.insert(tk.END, item[0], item[1])
                self.console.see(tk.END)
                self.user()
                return 'break'
            else:
                result = '\nИспользование: ls\n'

        elif cmd_name == 'cd':
            if len(command) == 1:
                result = self.shell.command_cd()
                self.console.insert(tk.END, '\n')
                self.console.see(tk.END)
                self.user()
                return 'break'
            elif len(command) >= 2:
                result = self.shell.command_cd(' '.join(command[1:]).rstrip())
                self.console.insert(tk.END, '\n')
                self.console.see(tk.END)
                self.user()
                return 'break'
            else:
                result = '\nИспользование: cd <папка_назначения>\n'

        elif cmd_name == 'pwd':
            if len(command) == 1:
                result = f'\n{self.shell.command_pwd()}\n'
            else:
                result = '\nИспользование: pwd\n'

        elif cmd_name == 'exit':
            if len(command) == 1:
                self.quit()
                return 'break'
            else:
                result = '\nИспользование: exit\n'

        elif cmd_name == 'chown':
            if len(command) == 3:
                result = self.shell.command_chown(command[1], command[2])
                self.console.insert(tk.END, '\n')
                self.console.see(tk.END)
                self.user()
                return 'break'
            else:
                result = '\nИспользование: chown <новый_владелец> <файл>\n'

        elif cmd_name == 'uniq':
            if len(command) == 2:
                result = self.shell.command_uniq(command[1])
                self.console.insert(tk.END, '\n')
                for item in result:
                    self.console.insert(tk.END, item)
                self.console.insert(tk.END, '\n')
                self.console.see(tk.END)
                self.user()
                return 'break'
            else:
                result = '\nИспользование: uniq <файл>\n'

        else:
            result = '\nНеизвестная команда, попробуйте снова!\n'
        
        self.console.insert(tk.END, result)
        self.console.see(tk.END)
        self.user()
        self.console.mark_set('insert', 'end')

        return 'break'

    def user(self):
        self.console.insert(tk.END, f'{self.shell.username}@localhost:~/{self.shell.current_dir}{self.shell.root} ')
        self.console.see(tk.END)
        self.console.mark_set('insert', 'end')


# Проверяем, что переданы аргументы
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Использование: py <название_программы.py> <имя_пользователя> <путь_к_архиву.zip>\n')
        sys.exit(1)

    username = sys.argv[1]
    zip_path = sys.argv[2]
    shell = ShellEmulator(username, zip_path)

    app = Application(shell)
    app.mainloop()
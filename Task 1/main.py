import zipfile
import sys
import tkinter as tk
from tkinter import scrolledtext


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
                lines = file.readlines()
                unique_lines = []
                previous_line = None

                for line in lines:
                    if line != previous_line:
                        unique_lines.append(line)
                        previous_line = line

                for unique_line in unique_lines:
                    res.append(unique_line.decode('utf8'))
            return res
        else:
            return(f'Ошибка: Неправильный путь {path}\n')

class Application(tk.Tk):
    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        self.title("Shell Emulator")
        self.geometry("800x600")
        self.configure(bg="#1e1e1e")

        # Создание текстовой области для вывода результатов
        self.output_area = scrolledtext.ScrolledText(self, bg="#2e2e2e", fg="#ffffff", font=("Consolas", 12))
        self.output_area.place(relx=0.5, rely=0.2, relwidth=0.9, relheight=0.7, anchor="n")

        # Поле для ввода команды
        self.entry = tk.Entry(self, bg="#2e2e2e", fg="#ffffff", font=("Consolas", 12))
        self.entry.place(relx=0.5, rely=0.05, relwidth=0.7, anchor="n")

        # Кнопка для выполнения команды
        execute_button = tk.Button(self, text="Execute", command=self.execute_command, bg="#4e4e4e", fg="#ffffff", font=("Consolas", 12))
        execute_button.place(relx=0.85, rely=0.05, anchor="n")

        self.output_area.tag_configure("OKBLUE", foreground="#0000ff")
        self.output_area.tag_configure("OKGREEN", foreground="#00ff00")
        self.output_area.tag_configure("WARNING", foreground="#ffcc00")
        self.output_area.tag_configure("FAIL", foreground="#ff0000")
        self.output_area.tag_configure("OKCYAN", foreground="#00ffff")
        self.output_area.tag_configure("HEADER", foreground="#ff66ff")
        self.output_area.tag_configure("BOLD", font=("Consolas", 12, "bold"))

    def execute_command(self):
        command = self.entry.get().split()
        self.output_area.insert(tk.END, f'{self.shell.username}@localhost:~/{self.shell.current_dir}{self.shell.root} {' '.join(command)}\n')

        if not command:
            return  # Пустая строка

        cmd_name = command[0]

        if cmd_name == 'ls':
            if len(command) == 1:
                result = self.shell.command_ls()
                for item in result:
                    self.output_area.insert(tk.END, item[0], item[1])
                self.entry.delete(0, tk.END)
                self.output_area.see(tk.END)
                return
            else:
                result = 'Использование: ls\n'

        elif cmd_name == 'cd':
            if len(command) == 1:
                result = self.shell.command_cd()
            elif len(command) == 2:
                result = self.shell.command_cd(' '.join(command[1:]).rstrip())
            else:
                result = 'Использование: cd <папка_назначения>\n'

        elif cmd_name == 'pwd':
            if len(command) == 1:
                result = self.shell.command_pwd()
            else:
                result = 'Использование: pwd\n'

        elif cmd_name == 'exit':
            if len(command) == 1:
                exit() #self.quit()
            else:
                result = 'Использование: exit\n'

        elif cmd_name == 'chown':
            if len(command) == 3:
                result = self.shell.command_chown(command[1], command[2])
            else:
                result = 'Использование: chown <новый_владелец> <файл>\n'

        elif cmd_name == 'uniq':
            if len(command) == 2:
                result = self.shell.command_uniq(command[1])
                for item in result:
                    self.output_area.insert(tk.END, item)
                self.entry.delete(0, tk.END)
                self.output_area.see(tk.END)
                return
            else:
                result = 'Использование: uniq <файл>\n'

        else:
            result = 'Неизвестная команда, попробуйте снова!\n'
        
        self.entry.delete(0, tk.END)
        self.output_area.insert(tk.END, result)
        self.output_area.see(tk.END)

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
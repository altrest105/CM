import unittest
from unittest.mock import patch, MagicMock
from main import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    @patch('zipfile.ZipFile')
    def setUp(self, mock_zipfile):
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ['Пусто/', 'Информатика/', 'Информатика/Отчёты/', 'Информатика/МетодичкаПоИнформатикеИИТ.pdf',
                                               'Информатика/ТребованияКОформлениюЭлектронныхОтчетовПоРаботам5-12.pdf', 'text.txt', 'prog.py',
                                               'cat.jpg', 'homework.zip', 'hello3.exe', 'words.txt', 'f.f']
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        self.shell = ShellEmulator('root', 'mock.zip')

    # Тесты для команды ls
    def test_ls_root(self):
        result = self.shell.command_ls()
        self.assertEqual(result, [['Пусто (owner: root)\n', 'BOLD'], ['Информатика (owner: root)\n', 'BOLD'], ['words.txt (owner: root)\n', 'OKBLUE'],
                                  ['text.txt (owner: root)\n', 'OKBLUE'], ['prog.py (owner: root)\n', 'OKGREEN'], ['homework.zip (owner: root)\n', 'FAIL'],
                                  ['hello3.exe (owner: root)\n', 'OKCYAN'], ['f.f (owner: root)\n', None], ['cat.jpg (owner: root)\n', 'WARNING']])

    def test_ls_directory(self):
        self.shell.command_cd('Информатика')
        result = self.shell.command_ls()
        self.assertEqual(result, [['ТребованияКОформлениюЭлектронныхОтчетовПоРаботам5-12.pdf (owner: root)\n', 'HEADER'], ['Отчёты (owner: root)\n', 'BOLD'],
                                  ['МетодичкаПоИнформатикеИИТ.pdf (owner: root)\n', 'HEADER']])

    def test_ls_empty_directory(self):
        self.shell.command_cd('Пусто')
        result = self.shell.command_ls()
        self.assertEqual(result, [])

    # Тесты для команды cd
    def test_cd_to_directory(self):
        self.shell.command_cd('Информатика')
        self.assertEqual(self.shell.current_dir, 'Информатика/')

    def test_cd_to_root(self):
        self.shell.command_cd('/Информатика/Отчёты')
        self.assertEqual(self.shell.current_dir, 'Информатика/Отчёты/')

    def test_cd_invalid_directory(self):
        result = self.shell.command_cd('cat.jpg')
        self.assertEqual('Ошибка: Неправильный путь cat.jpg\n', result)
        self.assertEqual(self.shell.current_dir, '')

    # Тесты для команды pwd
    def test_pwd_root(self):
        result = self.shell.command_pwd()
        self.assertEqual(result, '/root')

    def test_pwd_subdirectory(self):
        self.shell.command_cd('Информатика')
        result = self.shell.command_pwd()
        self.assertEqual(result, '/Информатика')

    def test_pwd_subsubdirectory(self):
        self.shell.command_cd('/Информатика/Отчёты')
        result = self.shell.command_pwd()
        self.assertEqual(result, '/Информатика/Отчёты')

    # Тесты для команды chown
    def test_chown_directory(self):
        self.shell.command_chown('user', 'Информатика')
        self.assertEqual(self.shell.file_owners['Информатика/'], 'user')

    def test_chown_absolute_path_file(self):
        self.shell.command_chown('user', '/Информатика/МетодичкаПоИнформатикеИИТ.pdf')
        self.assertEqual(self.shell.file_owners['Информатика/МетодичкаПоИнформатикеИИТ.pdf'], 'user')

    def test_chown_invalid_file(self):
        result = self.shell.command_chown('user', 'None')
        self.assertEqual(result, 'Ошибка: Неправильный путь None\n')

    # Тесты для команды uniq
    @patch('builtins.open', new_callable=MagicMock)
    def test_command_uniq_valid_file(self, mock_open):
        mock_file = MagicMock()
        mock_file.__enter__.return_value = [b'line1\n', b'line1\n', b'line2\n', b'line2\n', b'line3\n', b'line2\n']
        self.shell.archive.open.return_value = mock_file

        result = self.shell.command_uniq('words.txt')
        self.assertEqual(result, ['line1\n', 'line2\n', 'line3\n', 'line2\n'])
    
    @patch('builtins.open', new_callable=MagicMock)
    def test_command_uniq_notexist_file(self, mock_open):
        mock_file = MagicMock()
        mock_file.__enter__.return_value = [b'line1\n', b'line1\n', b'line2\n', b'line2\n', b'line3\n', b'line2\n']
        self.shell.archive.open.return_value = mock_file

        result = self.shell.command_uniq('not_exist.txt')
        self.assertEqual(result, 'Ошибка: Неправильный путь not_exist.txt\n')

    @patch('builtins.open', new_callable=MagicMock)
    def test_command_uniq_directory(self, mock_open):
        mock_file = MagicMock()
        mock_file.__enter__.return_value = [b'line1\n', b'line1\n', b'line2\n', b'line2\n', b'line3\n', b'line2\n']
        self.shell.archive.open.return_value = mock_file

        result = self.shell.command_uniq('Информатика')
        self.assertEqual(result, 'Ошибка: Неправильный путь Информатика\n')

if __name__ == '__main__':
    unittest.main()
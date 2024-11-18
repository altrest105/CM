import unittest
from io import StringIO
from unittest.mock import patch
from main import Assembler


class TestAssemblerCommands(unittest.TestCase):
    def setUp(self):
        self.assembler = Assembler(None, None, None)

    @patch("builtins.open")
    def test_all_commands(self, mock_open):
        mock_output = StringIO()
        mock_open.return_value.__enter__.return_value = mock_output

        commands = [
            "LOAD_CONST 6 295", # LOAD_CONST
            "READ_MEMORY 3 360", # READ_MEMORY
            "WRITE_MEMORY 2 597", # WRITE_MEMORY
            "BITREVERSE 1 907" # BITREVERSE
        ]

        # Обработка команд
        for command in commands:
            self.assembler.process_line(command)

        # Проверка сохраненных инструкций
        expected_instructions = [
            (6, 295),
            (3, 360),
            (2, 597),
            (1, 907)
        ]
        self.assertEqual(self.assembler.instructions, expected_instructions)

        # Генерация бинарного файла
        self.assembler.output_file = "mock_output"
        self.assembler.write_binary()

        # Проверка бинарного файла
        binary_output = mock_output.getvalue().strip()
        expected_binary = (
            "0xC0 0x09 0x38 0x00 0x00 \n" # LOAD_CONST
            "0x60 0x00 0x00 0x2D 0x00 \n" # READ_MEMORY
            "0x40 0x00 0x00 0x4A 0xA0 \n" # WRITE_MEMORY
            "0x20 0x00 0x00 0x71 0x60" # BITREVERSE
        )
        self.assertEqual(binary_output, expected_binary)


if __name__ == '__main__':
    unittest.main()
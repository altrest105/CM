import unittest
import yaml

from main import convert_value, convert_yaml, variables

class TestConfigProgram(unittest.TestCase):
    # Чистка переменных
    def setUp(self):
        variables.clear()

    # Тест преобразования чисел
    def test_convert_value_number(self):
        self.assertEqual(convert_value(42), 42)
        self.assertEqual(convert_value(3.14), 3.14)

    # Тест преобразования строки
    def test_convert_value_string(self):
        self.assertEqual(convert_value("Hello"), '@"Hello"')

    # Тест вычисления константы
    def test_convert_value_variable_reference(self):
        variables['timeout'] = 300
        self.assertEqual(convert_value("[timeout]"), '300')

    # Тест преобразования вложенного словаря
    def test_convert_value_nested_table(self):
        nested_dict = {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "username": "admin",
                "password": "secret"
            }
        }
        expected_output = (
            'table(\n'
            '\thost => @"localhost",\n'
            '\tport => 5432,\n'
            '\tcredentials => table(\n'
            '\t\tusername => @"admin",\n'
            '\t\tpassword => @"secret"\n'
            '\t)\n'
            ')'
        )
        self.assertEqual(convert_value(nested_dict), expected_output)

    # Тест на ошибку некорректного имени
    def test_invalid_name_error(self):
        yaml_data = {"123invalid": "value"}
        with self.assertRaises(ValueError) as cm:
            convert_yaml(yaml_data)
        self.assertEqual(str(cm.exception), 'Ошибка: Некорректное имя 123invalid')

    # Тест на ошибку несуществующей константы
    def test_undefined_constant_error(self):
        yaml_data = {"retry_delay": "[undefined_var]"}
        with self.assertRaises(ValueError) as cm:
            convert_yaml(yaml_data)
        self.assertEqual(str(cm.exception), 'Ошибка: Константа undefined_var не определена.')

    # Тест "Настройка базы данных"
    def test_database_config(self):
        yaml_content = """
        db:
            host: "localhost"
            port: 5432
            credentials:
                username: "admin"
                password: "secret"
        connection_timeout: 30
        max_connections: 100
        """
        yaml_data = yaml.safe_load(yaml_content)
        expected_output = (
            'var db table(\n'
            '\thost => @"localhost",\n'
            '\tport => 5432,\n'
            '\tcredentials => table(\n'
            '\t\tusername => @"admin",\n'
            '\t\tpassword => @"secret"\n'
            '\t)\n'
            ');\n'
            'var connection_timeout 30;\n'
            'var max_connections 100;'
        )
        result = convert_yaml(yaml_data)
        self.assertEqual(result.strip(), expected_output)

# Тест "Конфигурация веб-приложения"
    def test_web_app_config(self):
        yaml_content = """
        is_debug: true
        app:
            name: "MyWebApp"
            version: 1.0
            debug_mode: "[is_debug]"
        logging:
            level: "INFO"
            file_path: "/var/log/app.log"
        """
        yaml_data = yaml.safe_load(yaml_content)
        expected_output = (
            'var is_debug True;\n'
            'var app table(\n'
            '\tname => @"MyWebApp",\n'
            '\tversion => 1.0,\n'
            '\tdebug_mode => True\n'
            ');\n'
            'var logging table(\n'
            '\tlevel => @"INFO",\n'
            '\tfile_path => @"/var/log/app.log"\n'
            ');'
        )
        result = convert_yaml(yaml_data)
        self.assertEqual(result.strip(), expected_output)

    # Тест "устройство умного дома"
    def test_iot_device_config(self):
        yaml_content = """
        device:
            id: "sensor_001"
            type: "temperature"
            location:
                room: "Living Room"
                floor: 1
        settings:
            interval: 10
            units: "Celsius"
        """
        yaml_data = yaml.safe_load(yaml_content)
        expected_output = (
            'var device table(\n'
            '\tid => @"sensor_001",\n'
            '\ttype => @"temperature",\n'
            '\tlocation => table(\n'
            '\t\troom => @"Living Room",\n'
            '\t\tfloor => 1\n'
            '\t)\n'
            ');\n'
            'var settings table(\n'
            '\tinterval => 10,\n'
            '\tunits => @"Celsius"\n'
            ');'
        )
        result = convert_yaml(yaml_data)
        self.assertEqual(result.strip(), expected_output)



if __name__ == "__main__":
    unittest.main()

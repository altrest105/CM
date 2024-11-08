import sys
import yaml
import re

def is_name(name):
    return re.match(r'^[_a-z]+$', name)

def convert_value(value):
    if isinstance(value, dict):
        return 'table(\n' + ',\n'.join(f'{key} => {convert_value(value)}' for key, value in value.items()) + '\n)'
    elif isinstance(value, str):
        return f'@"{value}"'
    elif isinstance(value, (int, float)):
        return value
    else:
        raise ValueError

def convert_yaml():
    exit()

def main():
    if len(sys.argv) != 2:
        print('Использование: python main.py <путь_к_yaml_файлу>')
        sys.exit(1)

    input_path = sys.argv[1]
    try:
        with open(input_path) as file:
            yaml_data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f'Файл {input_path} не найден')
    except yaml.YAMLError as error:
        print(f'Ошибка в yaml: {error}')
    except ValueError as error:
        print(f'Ошибка конвертации: {error}')
    
    print(yaml_data)

if __name__ == '__main__':
    main()
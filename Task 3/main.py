import sys
import yaml
import re

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
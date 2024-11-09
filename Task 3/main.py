import sys
import yaml
import re

variables = {}

def is_name(name):
    return re.match(r'^[_a-z]+$', name)

def convert_value(value, indent_level=1):
    indent = '\t' * indent_level
    if isinstance(value, dict):
        inner = ',\n'.join(f'{indent}{key} => {convert_value(val, indent_level + 1)}' for key, val in value.items())
        return f'table(\n{inner}\n{"\t" * (indent_level - 1)})'
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        var_name = value[1:-1]
        if var_name in variables:
            return str(variables[var_name])
        else:
            raise ValueError(f"Ошибка: Константа {var_name} не определена.")
    elif isinstance(value, str):
        return f'@"{value}"'
    else:
        raise ValueError(f'Ошибка: Неподдерживаемый тип значения {type(value)}')

def convert_yaml(yaml_data):
    result = []
    for key, value in yaml_data.items():
        if not is_name(key):
            raise ValueError(f'Ошибка: Некорректное имя {key}')
        
        if isinstance(value, (int, float, str)) and not (isinstance(value, str) and value.startswith("[") and value.endswith("]")):
            variables[key] = value

        result.append(f'var {key} {convert_value(value)};')
    return '\n'.join(result)

def main():
    if len(sys.argv) != 2:
        print('Использование: python <программа.py> <файл.yaml>')
        sys.exit(1)

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            yaml_data = yaml.safe_load(file)
        
        result = convert_yaml(yaml_data)
        print(result)
        
    except FileNotFoundError:
        print(f'Ошибка файла: {input_path} не найден')
    except yaml.YAMLError as error:
        print(f'Ошибка в формате yaml: {error}')
    except ValueError as error:
        print(f'Ошибка преобразования: {error}')

if __name__ == '__main__':
    main()

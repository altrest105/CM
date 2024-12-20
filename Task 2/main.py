import requests
import re
import yaml
import subprocess
import time

# Получение ответа в виде HTML
def get_package_info(package, distro):
    url = f'https://packages.ubuntu.com/{distro}/{package}'
    MAX_RETRIES = 10
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 500:
                print(f"Ошибка 500 (внутренняя ошибка сервера) при запросе {package}. Попытка {attempt + 1}/{MAX_RETRIES}.")
            else:
                print(f"Ошибка {response.status_code} при запросе {package}.")
                break
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети при запросе {package}: {e}")
        
        time.sleep(5)
    
    raise Exception(f"Не удалось получить данные о пакете {package} после {MAX_RETRIES} попыток.")

# Получение отсортированного списка зависимостей пакета
def get_depends(info):
    start = info.find('<ul class="uldep">\n')
    end = info.find('</div> <!-- end pdeps -->')
    info = info[start:end]

    pattern = r'<dt><span class="nonvisual">dep:</span>\s*<a href="[^"]*/[^"]*/([^"]*)"'
    matches = set(re.findall(pattern, info))
    return sorted(list(matches))


# Создание графа
def build_dependency_graph(package, graph, visited, distro):
    if package in visited:
        return
    
    visited.add(package)
    package_info = get_package_info(package, distro)
    dependencies = get_depends(package_info)
    
    for dep in dependencies:
        graph.append((package, dep))
        build_dependency_graph(dep, graph, visited, distro)

# Генерация PlantUML файла для графа зависимостей
def generate_plantuml(graph, package):
    uml = "@startuml\n"
    uml += "skinparam linetype ortho\n"
    if len(graph) == 0:
        uml += f'"{package}"\n'
    else:
        for parent, child in graph:
            uml += f'"{parent}" --> "{child}"\n'
    
    uml += "@enduml\n"
    return uml

# Чтение конфигурационного файла
def read_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Получение пакета и дистрибутива из URL-адреса репозитория
def extract_distro_and_package(url):
    pattern = r'https://packages.ubuntu.com/([^/]+)/([^/]+)'
    match = re.search(pattern, url)
    
    if match:
        distro = match.group(1) 
        package = match.group(2)
        return distro, package
    else:
        raise ValueError("Неверный формат URL")

def main(config_file):
    config = read_config(config_file)

    plantuml_path = config['visualizer_path']  # Путь к программе визуализации
    package_path = config['package_path']  # Путь к пакету для анализа
    repository = config['repository'] # Репозиторий пакета

    distro, package_name = extract_distro_and_package(repository)

    graph = []
    visited = set()
    build_dependency_graph(package_name, graph, visited, distro)
    
    plantuml_content = generate_plantuml(graph, package_name)

    with open('dependencies.puml', 'w') as file:
        file.write(plantuml_content)

    subprocess.run([plantuml_path, 'dependencies.puml'])

if __name__ == '__main__':
    main('config.yaml')
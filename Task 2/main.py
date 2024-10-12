import requests
import re

#Получение ответа в виде HTML
def get_package_info(package):
    url = f'https://packages.ubuntu.com/focal/{package}'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Ошибка при запросе: {response.status_code}")
    return response.text

#Получение отсортированного списка зависимостей пакета
def get_depends(info):
    start = info.find('<ul class="uldep">\n')
    end = info.find('</div> <!-- end pdeps -->')
    info = info[start:end]
    print(info)

    pattern = r'<dt><span class="nonvisual">dep:</span>\n\t<a href="[^"]*/[^"]*/([^"]*)"'
    matches = set(re.findall(pattern, info))
    return sorted(list(matches))


package_info = get_package_info('curl')
depends = get_depends(package_info)
print(depends)
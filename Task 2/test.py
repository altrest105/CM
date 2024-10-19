import unittest
from unittest.mock import patch, MagicMock

# Импортируем функции для тестирования
from main import get_package_info, get_depends, extract_distro_and_package, generate_plantuml, build_dependency_graph

class TestDependencyTool(unittest.TestCase):
    # Проверка ответа с кодом 200
    @patch('requests.get')
    def test_get_package_info_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "HTML content"
        mock_get.return_value = mock_response
        
        result = get_package_info('curl', 'focal')
        self.assertEqual(result, "HTML content")

    # Проверка ответа с 500, потом 200
    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    @patch('builtins.print')
    def test_get_package_info_retry_on_500(self, mock_print, mock_sleep, mock_get):
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.text = "HTML content"

        mock_get.side_effect = [mock_response_500, mock_response_200]

        result = get_package_info('curl', 'focal')
        self.assertEqual(result, "HTML content")
        self.assertEqual(mock_get.call_count, 2)  # Проверяем, что было 2 попытки
        mock_sleep.assert_called() # Проверяем, что time.sleep вызывался
        mock_print.assert_called()  # Проверяем, что print вызывался (если это важно)

    # Проверка ответа с кодом 500
    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    @patch('builtins.print')
    def test_get_package_info_fail_after_retries(self, mock_print, mock_sleep, mock_get):
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500
        mock_get.return_value = mock_response_500
        

        with self.assertRaises(Exception):
            get_package_info('curl', 'focal')
        self.assertEqual(mock_get.call_count, 10)  # Проверяем, что было 10 попыток
        mock_sleep.assert_called() # Проверяем, что time.sleep вызывался
        mock_print.assert_called()  # Проверяем, что print вызывался (если это важно)


    def test_get_depends(self):
        # Пример HTML с зависимостями
        html_data = '''
        <div class="pdeps">
            <ul class="uldep">
                <dt><span class="nonvisual">dep:</span>\n\t
                <a href="/focal/packageB">packageB</a></dt>\n
                <dt><span class="nonvisual">dep:</span>\n\t
                <a href="/focal/packageC">packageC</a></dt>\n
                <dt><span class="nonvisual">dep:</span>\n\t
                <a href="/focal/packageD">packageD</a></dt>\n
            </ul>
        </div> <!-- end pdeps -->
        '''

        expected_dependencies = ['packageB', 'packageC', 'packageD']

        result = get_depends(html_data)

        self.assertListEqual(result, expected_dependencies)

    # Тест построения графа
    @patch('main.get_package_info')
    @patch('main.get_depends')
    def test_build_dependency_graph(self, mock_get_depends, mock_get_package_info):
        package = 'packageA'
        distro = 'noble'
        mock_get_package_info.side_effect = [
            '<html>...</html>',
            '<html>...</html>',
            '<html>...</html>',
            '<html>...</html>',
        ]

        mock_get_depends.side_effect = [
            ['packageB', 'packageC'],
            ['packageD'],
            [],
            []
        ]

        graph = []
        visited = set()

        build_dependency_graph(package, graph, visited, distro)

        expected_graph = [
            ('packageA', 'packageB'),
            ('packageB', 'packageD'),
            ('packageA', 'packageC')
        ]

        self.assertListEqual(graph, expected_graph)

        expected_visited = {'packageA', 'packageB', 'packageC', 'packageD'}
        self.assertSetEqual(visited, expected_visited)

    # Тест получения пакета и дистро из url
    def test_extract_distro_and_package(self):
        url = "https://packages.ubuntu.com/noble/curl"
        distro, package = extract_distro_and_package(url)
        self.assertEqual(distro, 'noble')
        self.assertEqual(package, 'curl')

    # Тест с пустым графом
    def test_generate_plantuml_empty_graph(self):
        graph = []
        package = "gcc"
        result = generate_plantuml(graph, package)
        expected_output = '@startuml\nskinparam linetype ortho\n"gcc"\n@enduml\n'
        self.assertEqual(result, expected_output)

    # Тест с заполненным графом
    def test_generate_plantuml_with_graph(self):
        graph = [("gcc", "libc6"), ("gcc", "libcurl4")]
        package = "gcc"
        result = generate_plantuml(graph, package)
        expected_output = '@startuml\nskinparam linetype ortho\n"gcc" --> "libc6"\n"gcc" --> "libcurl4"\n@enduml\n'
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
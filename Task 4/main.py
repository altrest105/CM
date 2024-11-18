import xml.etree.ElementTree as ET
import sys


class Assembler:
    def __init__(self, input_file, output_file, log_file):
        self.input_file = input_file
        self.output_file = output_file
        self.log_file = log_file
        self.instructions = []

    def assemble(self):
        with open(self.input_file, 'r') as f:
            for line in f:
                self.process_line(line.strip())

        self.write_binary()
        self.write_log()

    # Обработка строки, добавление её в список инструкций
    def process_line(self, line):
        if not line:
            return 
        parts = line.split()
        command, a, b = parts[0].upper(), int(parts[1]), int(parts[2])
        if (command == 'LOAD_CONST') and (a == 6):
            self.instructions.append((a, b))
        elif (command == 'READ_MEMORY') and (a == 3):
            self.instructions.append((a, b))
        elif (command == 'WRITE_MEMORY') and (a == 2):
            self.instructions.append((a, b))
        elif (command == 'BITREVERSE') and (a == 1):
            self.instructions.append((a, b))
        else:
            raise ValueError(f'Неизвестная команда: {command}')

    # Перевод числа в двоичную систему
    def int_to_bin(self, number, bits):
        values = {'3': 7, '18': 262143, '32': 4294967295}
        min_value = 0
        max_value = values[str(bits)]
        if (number > max_value) or (number < min_value):
            raise ValueError(f'Число {number} выходит за пределы: [{min_value}, {max_value}]')
        return bin(number)[2:].zfill(bits)

    # Запись в "бинарный" файл
    def write_binary(self):
        with open(self.output_file, 'w') as f:
            for a, b in self.instructions:
                a_field = self.int_to_bin(a, 3)

                if a == 6:
                    b_field = self.int_to_bin(b, 18)
                    instruction = a_field + b_field + '0' * 19
                    instruction_parts = [hex(int(instruction[i:i+8], 2))[2:].upper().zfill(2) for i in range(0, len(instruction), 8)]
                    for byte in instruction_parts:
                        f.write(f'0x{byte} ')
                    f.write('\n')
                else:
                    b_field = self.int_to_bin(b, 32)
                    instruction = a_field + b_field + '0' * 5
                    instruction_parts = [hex(int(instruction[i:i+8], 2))[2:].upper().zfill(2) for i in range(0, len(instruction), 8)]
                    for byte in instruction_parts:
                        f.write(f'0x{byte} ')
                    f.write('\n')

    # Запись в лог файл
    def write_log(self):
        root = ET.Element('log')
        for i, (a, b) in enumerate(self.instructions):
            instr = ET.SubElement(root, 'instruction', id=str(i))
            ET.SubElement(instr, 'a').text = str(a)
            ET.SubElement(instr, 'b').text = str(b)

        tree = ET.ElementTree(root)
        tree.write(self.log_file)


class Interpreter:
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_range = memory_range
        self.memory = ['0'] * 1024
        self.accumulator = 0

    def execute(self):
        instructions = []
        with open(self.binary_file, 'r') as f:
            for line in f:
                instruction = line.strip()
                instructions.append(instruction)

        instructions = self.hex_to_bin(instructions)
        self.execute_instructions(instructions)

        self.write_results(self.result_file, self.memory_range)
    
    # Перевод из 16-ричной записи в двоичную строку
    def hex_to_bin(self, bytes):
        bytes = ' '.join(bytes).replace('0x', '').replace(' ', '')
        hex_to_bin_map = {
            '0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101',
            '6': '0110', '7': '0111', '8': '1000', '9': '1001', 'A': '1010', 'B': '1011',
            'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'
        }
        binary = ''
        for s in bytes:
            binary += hex_to_bin_map[s]
        return binary

    # Выполнение инструкций
    def execute_instructions(self, binary):
        i = 0
        while i < len(binary):
            a = int(binary[i:i + 3], 2)
            i += 3

            if a == 6: # LOAD_CONST
                b = int(binary[i:i + 18], 2)
                i += 37
                self.load_const(a, b)
            
            elif a == 3: # READ_MEMORY
                b = int(binary[i:i + 32], 2)
                i += 37
                self.read_memory(a, b)
            
            elif a == 2: # WRITE_MEMORY
                b = int(binary[i:i + 32], 2)
                i += 37
                self.write_memory(a, b)
            
            elif a == 1: # BITREVERSE
                b = int(binary[i:i + 32], 2)
                i += 37
                self.bit_reverse(a, b)
            else:
                raise ValueError(f'Неизвестная команда: {a}')

    # LOAD_CONST
    def load_const(self, a, b):
        print(f"LOAD_CONST: a={a}, b={b}")
        self.accumulator = bin(b)[2:]
    
    #READ_MEMORY
    def read_memory(self, a, b):
        print(f"READ_MEMORY: a={a}, b={b}")
        self.accumulator = self.memory[b]
    
    #WRITE_MEMORY
    def write_memory(self, a, b):
        print(f"WRITE_MEMORY: a={a}, b={b}")
        self.memory[b] = self.accumulator

    #BITREVERSE
    def bit_reverse(self, a, b):
        print(f"BITREVERSE: a={a}, b={b}")
        self.accumulator = self.memory[b][::-1]

    # Запись результатов
    def write_results(self, result_file, memory_range):
        root = ET.Element("results")
        for i in range(*memory_range):
            mem = ET.SubElement(root, "memory", address=str(i))
            mem.text = str(self.memory[i])

        tree = ET.ElementTree(root)
        tree.write(result_file)


if __name__ == '__main__':
    if len(sys.argv) != 7:
        print('Использование: py <входной_файл> <бинарный_файл> <лог_файл> <файл_результат> <старт_памяти> <конец_памяти>')
        sys.exit(1)

    input_file = sys.argv[1]
    binary_file = sys.argv[2]
    log_file = sys.argv[3]
    result_file = sys.argv[4]
    memory_start = int(sys.argv[5])
    memory_end = int(sys.argv[6])


    assembler = Assembler(input_file, binary_file, log_file)
    assembler.assemble()

    interpreter = Interpreter(binary_file, result_file, (memory_start, memory_end))
    interpreter.execute()
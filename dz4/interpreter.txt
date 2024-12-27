import yaml


class Interpreter:
    def __init__(self, path_to_bin, limit):
        self.registers = [0] * limit
        self.code = 0
        try:
            with open(path_to_bin, 'rb') as file:
                self.code = int.from_bytes(file.read(), byteorder='little', signed=True)
        except FileNotFoundError:
            print('Файл не найден')

    def interpret(self):
        while self.code != 0:
            a = self.code & ((1 << 5) - 1)
            match a:
                case 6:
                    self.load_constant()
                case 2:
                    self.read_memory()
                case 17:
                    self.write_memory()
                case 23:
                    self.lte()
                case _:
                    self.code >>= 1
        self.dump_result()

    def dump_result(self):
        with open('result.yaml', 'w') as file:
            results = {'registers': []}

            for ind, val in enumerate(self.registers):
                if val > 2 ** 18 - 1:
                    val ^= (1 << 19) - 1
                    val = -val - 1
                results['registers'].append({'register': ind, 'value': val})
            yaml.dump(results, file)

    def load_constant(self):
        b = (self.code & ((1 << 19) - 1)) >> 5
        c = (self.code & ((1 << 25) - 1)) >> 19
        self.code >>= 56

        self.registers[c] = b

    def read_memory(self):
        b = (self.code & ((1 << 11) - 1)) >> 5
        c = (self.code & ((1 << 35) - 1)) >> 11
        self.code >>= 56

        self.registers[b] = self.registers[c]

    def write_memory(self):
        b = (self.code & ((1 << 29) - 1)) >> 5
        c = (self.code & ((1 << 35) - 1)) >> 29
        self.code >>= 56

        self.registers[b] = self.registers[c]

    def lte(self):
        b = (self.code & ((1 << 10) - 1)) >> 5
        c = (self.code & ((1 << 17) - 1)) >> 11
        self.code >>= 56

        val1 = self.registers[b]
        val2 = self.registers[c]

        self.registers[b] = int(val1 <= val2)

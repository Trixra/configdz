import yaml


class Assembler:
    def __init__(self, path_to_code, path_to_log):
        self.path_to_log = path_to_log
        self.logs = []
        self.commands = []
        try:
            with open(path_to_code, 'rt') as file:
                self.commands = file.readlines()
        except FileNotFoundError:
            print('Файл не найден')
        except:
            print('Ошибка работы с файлом')

    def assemble(self, path_to_bin):
        with open(path_to_bin, 'wb') as file:
            for command in self.commands:
                if command.strip().startswith('#'):
                    continue

                try:
                    name, body = command.split(' ', 1)
                except ValueError:
                    continue

                body = tuple(map(int, body.split()))
                number = None
                bits = None
                match name:
                    case 'CONST':
                        number = 6
                        bits = Assembler.load_constant(*body)
                    case 'READ':
                        number = 2
                        bits = Assembler.read_memory(*body)
                    case 'WRITE':
                        number = 17
                        bits = Assembler.write_memory(*body)
                    case 'LTE':
                        number = 23
                        bits = Assembler.lte(*body)
                file.write(bits)
                self.logs.append([number, body, bits])
        self.make_log()

    def make_log(self):
        with open(self.path_to_log, 'w') as file:
            logs = {'tests': []}
            for log in self.logs:
                key = []
                for name, param in zip('ABCD', [log[0], *log[1]]):
                    key.append(f'{name}={param}')
                logs['tests'].append({'test': '   '.join(key), 'value': ' '.join(hex(i) for i in log[-1])})
            yaml.dump(logs, file)

    @staticmethod
    def load_constant(b, c):
        bits = (c << 19) | (b << 5) | 6
        return bits.to_bytes(7, byteorder='little', signed=True)

    @staticmethod
    def read_memory(b, c):
        bits = (c << 11) | (b << 5) | 2
        return bits.to_bytes(7, byteorder='little', signed=True)

    @staticmethod
    def write_memory(b, c):
        bits = (c << 29) | (b << 5) | 17
        return bits.to_bytes(7, byteorder='little', signed=True)

    @staticmethod
    def lte(b, c):
        bits = (c << 11) | (b << 5) | 23
        return bits.to_bytes(7, byteorder='little', signed=True)

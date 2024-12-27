import os
import time
import zipfile
import tkinter as tk
from tkinter import scrolledtext
import tempfile
import shutil
import xml.etree.ElementTree as ET
import logging

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Установите уровень логирования

# Создание обработчика для записи логов в файл
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)  # Установите уровень логирования для обработчика

# Создание форматера для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(file_handler)

class Emulator:
    """
    Класс для эмуляции файловой системы и выполнения команд, аналогичных shell-командам.

    Атрибуты:
        config (dict): Конфигурационные параметры, загруженные из XML-файла.
        vfs_path (str): Путь к zip-файлу с виртуальной файловой системой.
        startup_script (str): Путь к стартовому скрипту, который выполняется при запуске.
        current_dir (str): Текущая рабочая директория в виртуальной файловой системе.
        root_dir (str): Корневая директория распакованной виртуальной файловой системы.
        temp_dir (str): Временная директория для распакованной виртуальной файловой системы.
        start_time (float): Время запуска эмулятора для расчета uptime.
    """

    def __init__(self, config_path):
        """
        Инициализирует эмулятор, загружает конфигурацию и виртуальную файловую систему.

        Параметры:
            config_path (str): Путь к XML-конфигурационному файлу.
        """
        self.config = self.read_config(config_path)
        self.vfs_path = self.config['vfs_path']
        self.startup_script = self.config['startup_script']

        self.current_dir = ''
        self.init_vfs()

        self.start_time = time.time()  # Время старта для расчета uptime
        logger.debug('Emulator started')

    def read_config(self, config_path):
        """
        Читает конфигурационный файл в формате XML и возвращает параметры.

        Параметры:
            config_path (str): Путь к XML-файлу.

        Возвращает:
            dict: Словарь с параметрами конфигурации.
        """
        tree = ET.parse(config_path)
        root = tree.getroot()
        vfs_path = root.find('vfs_path').text
        startup_script = root.find('startup_script').text
        logger.debug('Config read: vfs_path=%s, startup_script=%s', vfs_path, startup_script)
        return {'vfs_path': vfs_path, 'startup_script': startup_script}

    def init_vfs(self):
        """
        Инициализирует виртуальную файловую систему: открывает ZIP-файл.
        """
        self.zip_ref = zipfile.ZipFile(self.vfs_path, 'r')
        logger.debug('VFS initialized: vfs_path=%s', self.vfs_path)

    def run_startup_script(self):
        """
        Выполняет команды, указанные в стартовом скрипте, при запуске эмулятора.
        """
        script_path = os.path.join(self.current_dir, self.startup_script)
        if script_path in self.zip_ref.namelist():
            with self.zip_ref.open(script_path) as script_file:
                commands = script_file.readlines()
                for command in commands:
                    self.run_command(command.strip().decode('utf-8'))

    def cleanup(self):
        """
        Очищает временную директорию после завершения работы эмулятора.
        """
        logger.debug('Cleaning up...')
        self.zip_ref.close()

    def run_command(self, command, output_widget=None):
        """
        Выполняет указанную команду и выводит результат.

        Параметры:
            command (str): Команда для выполнения.
            output_widget (tk.Text, optional): Виджет для вывода результата в GUI.
        """
        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        if output_widget:
            # Вывод текущей директории перед командой, как в реальном терминале
            output_widget.insert(tk.END, f"{self.whoami()}$ {command}\n")

        # Выполнение команды
        if cmd == 'ls':
            result = self.ls()
        elif cmd == 'cd':
            if args:
                result = self.cd(args[0])
            else:
                result = "cd: missing path"
        elif cmd == 'exit':
            result = self.exit()
        elif cmd == 'date':
            result = self.date()
        elif cmd == 'whoami':
            result = self.whoami()
        elif cmd == 'uptime':
            result = self.uptime()
        else:
            result = f"{cmd}: command not found"

        # Вывод результата команды
        if output_widget:
            output_widget.insert(tk.END, result + "\n")
            output_widget.see(tk.END)  # Автопрокрутка вниз

        logger.debug('Command executed: %s', command)

    def ls(self):
        """
        Выполняет команду 'ls': выводит список файлов и директорий в текущей директории.

        Возвращает:
            str: Список файлов и директорий.
        """
        logger.debug('Listing files in current directory: %s', self.current_dir)
        files = [f for f in self.zip_ref.namelist() if f.startswith(self.current_dir)]
        current_dir_files = set()

        for f in files:
            relative_path = f.replace(self.current_dir, '', 1).lstrip('/')
            if '/' not in relative_path:
                current_dir_files.add(relative_path)
            else:
                dir_name = relative_path.split('/')[0]
                current_dir_files.add(dir_name)

        return "\n".join(sorted(current_dir_files))


    def cd(self, path):
        """
        Выполняет команду 'cd': изменяет текущую рабочую директорию.

        Параметры:
            path (str): Путь к новой директории.

        Возвращает:
            str: Сообщение о результате операции.
        """
        logger.debug('Changing directory: %s', path)

        if path == '..':
            if self.current_dir:
                self.current_dir = os.path.normpath(os.path.join(self.current_dir, '..'))
                if self.current_dir == '.':
                    self.current_dir = ''
            return f"Changed directory to {self.current_dir}"
        else:
            new_path = os.path.join(self.current_dir, path)
            if not new_path.endswith('/'):
                new_path += '/'

            if any(name.startswith(new_path) for name in self.zip_ref.namelist()):
                self.current_dir = new_path
                return f"Changed directory to {self.current_dir}"
            else:
                return f"cd: {path}: No such file or directory"


    def exit(self):
        """
        Выполняет команду 'exit': завершает работу эмулятора.

        Возвращает:
            str: Сообщение о завершении работы.
        """
        logger.debug('Exiting emulator...')
        self.cleanup()
        exit()
        return "Exiting emulator..."

    def date(self):
        """
        Выполняет команду 'date': выводит текущую дату и время.

        Возвращает:
            str: Текущая дата и время.
        """
        logger.debug('Getting current date and time...')
        import datetime
        return str(datetime.datetime.now())

    def whoami(self):
        """
        Выполняет команду 'whoami': выводит имя текущего пользователя.

        Возвращает:
            str: Имя пользователя.
        """
        logger.debug('Getting current user...')
        return os.getlogin()

    def uptime(self):
        """
        Выполняет команду 'uptime': выводит время работы эмулятора.

        Возвращает:
            str: Время работы эмулятора в секундах.
        """
        logger.debug('Getting uptime...')
        uptime_seconds = time.time() - self.start_time
        return f"Uptime: {uptime_seconds:.2f} seconds"


class ShellGUI:
    """
    Класс для создания GUI оболочки, которая позволяет вводить команды и видеть результат их выполнения.

    Атрибуты:
        emulator (Emulator): Объект эмулятора, управляющий командной оболочкой.
        root (tk.Tk): Корневое окно приложения.
        output (tk.scrolledtext.ScrolledText): Текстовое поле для вывода результатов команд.
        entry (tk.Entry): Поле ввода для команд.
    """
    
    def __init__(self, emulator):
        """
        Инициализация GUI для эмулятора.

        Параметры:
            emulator (Emulator): Объект эмулятора, управляющий командной оболочкой.
        """
        logger.debug('Initializing GUI...')
        self.emulator = emulator
        self.root = tk.Tk()
        self.root.title("Shell Emulator")

        # Текстовое поле для вывода
        self.output = scrolledtext.ScrolledText(self.root, height=20, width=80, state=tk.NORMAL)
        self.output.pack()

        # Поле ввода для команд
        self.entry = tk.Entry(self.root, width=80)
        self.entry.pack()
        self.entry.bind('<Return>', self.execute_command)

        # Выполняем стартовый скрипт
        self.emulator.run_startup_script()

    def execute_command(self, event):
        """
        Обработчик ввода команды: выполняет команду и выводит результат.

        Параметры:
            event (tk.Event): Событие нажатия клавиши <Return>.
        """
        logger.debug('Executing command: %s', self.entry.get())
        command = self.entry.get()
        self.emulator.run_command(command, output_widget=self.output)
        self.entry.delete(0, tk.END)

    def run(self):
        """
        Запуск главного цикла GUI.
        """
        logger.debug('Starting GUI main loop...')
        self.root.mainloop()


if __name__ == '__main__':
    config_path = 'config.xml'  # Путь к конфигурационному файлу
    emulator = Emulator(config_path)
    gui = ShellGUI(emulator)
    gui.run()

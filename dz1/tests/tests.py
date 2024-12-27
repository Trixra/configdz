import unittest
from core import Emulator
import shutil
import os
import time

class TestEmulator(unittest.TestCase):
    def setUp(self):
        self.emulator = Emulator('config.xml')


    def test_whoami(self):
        """
        Тест команды whoami: проверка вывода имени пользователя.
        """
        result = self.emulator.whoami()
        expected_user = os.getlogin()
        self.assertEqual(result, expected_user)

    def test_uptime(self):
        """
        Тест команды uptime: проверка корректного расчета времени работы эмулятора.
        """
        start_time = self.emulator.start_time
        time.sleep(1)  # Ждем немного для проверки времени
        result = self.emulator.uptime()
        uptime_seconds = time.time() - start_time
        self.assertIn("Uptime", result)
        self.assertAlmostEqual(float(result.split()[1]), uptime_seconds, delta=1)

    def test_run_ls_command(self):
        """
        Тест команды ls через run_command.
        """
        self.emulator.run_command('ls')
        output = self.emulator.ls()
        self.assertIn('startup.sh', output)

    def test_run_cd_command(self):
        """
        Тест команды cd через run_command.
        """
        self.emulator.run_command('cd folder1')
        self.assertTrue(self.emulator.current_dir.endswith('folder1'))

    def test_run_date_command(self):
        """
        Тест команды date через run_command.
        """
        output = self.emulator.date()
        current_date = time.strftime("%Y-%m-%d")
        self.assertIn(current_date, output)

    def test_run_whoami_command(self):
        """
        Тест команды whoami через run_command.
        """
        output = self.emulator.whoami()
        self.assertEqual(output, os.getlogin())

    def test_run_uptime_command(self):
        """
        Тест команды uptime через run_command.
        """
        start_time = self.emulator.start_time
        time.sleep(1)  # Ждем немного для проверки времени
        result = self.emulator.uptime()
        uptime_seconds = time.time() - start_time
        self.assertIn("Uptime", result)
        self.assertAlmostEqual(float(result.split()[1]), uptime_seconds, delta=1)


if __name__ == '__main__':
    unittest.main()
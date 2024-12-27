## Клонирование репозитория
Склонируйте репозиторий с исходным кодом и тестами:
```bash
git clone https://github.com/xartd0/conf_upravlenie.git
cd conf_upravlenie
```

## Установка зависимостей 
Активириуем виртуальное окружение
```bash
# Активируйте виртуальное окружение
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для MacOS/Linux:
source venv/bin/activate
```

## Запуск
Запуск эмулятора
```bash
python core.py
```

## Структура проекта
```bash
test
 - tests.py # тесты
app.log # логи проекта
config.xml # конфиг для эмулятора
core.py # ядро эмулятора
generate_virtual_fs.py # генерирует виртуальное пространство
```

## Запуск тестов
```bash
python -m tests.tests
```
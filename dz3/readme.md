
# Конвертер XML в конфигурационный язык

Этот проект предоставляет инструмент командной строки на Python, который преобразует XML файлы в собственный конфигурационный язык. Этот язык поддерживает различные конструкции, такие как комментарии, массивы, словари, константы и многое другое. Инструмент обнаруживает и обрабатывает синтаксические ошибки, предоставляя пользователю информативные сообщения об ошибках.

## Особенности

- **Структуры**: XML элементы конвертируются в объекты структуры.
- **Массивы**: Повторяющиеся XML элементы с одинаковыми тегами конвертируются в массивы.
- **Константы**: Поддержка объявления и вычисления констант на этапе трансляции.
- **Обработка ошибок**: Надежная обработка ошибок при отсутствии атрибутов или неизвестных констант.
- **Тестирование**: Комплексное тестирование с использованием `pytest` для проверки всех конструкций и преобразований.

## Использование

### Установка

Убедитесь, что у вас установлена версия Python 3.7 или выше.

1. Клонируйте этот репозиторий:

    ```bash
    git clone https://github.com/xartd0/conf_upravlenie
    cd conf_upravlenie
    ```

2. Установите зависимости (если они есть):

    ```bash
    pip install -r requirements.txt
    ```

### Использование инструмента командной строки

Вы можете использовать конвертер, указав путь к XML файлу:

```bash
python converter.py -f input.xml
```

Это команда прочитает файл `input.xml` и выведет соответствующую структуру на конфигурационном языке в стандартный вывод.

#### Пример

Для XML файла следующего вида:

```xml
<server port="8080">
  <host>localhost</host>
  <routes>
    <route path="/home" handler="homeHandler"/>
    <route path="/login" handler="loginHandler"/>
  </routes>
  <const name="MAX_CONNECTIONS" value="100"/>
  <compute name="MAX_CONNECTIONS"/>
</server>
```

Запуск команды:

```bash
python converter.py -f server_config.xml
```

Вернет результат:

```plaintext
struct {
  port = 8080,
  host = "localhost",
  routes = struct {
    route = (list
      struct {
        path = "/home",
        handler = "homeHandler"
      }
      struct {
        path = "/login",
        handler = "loginHandler"
      }
    )
  },
  const = 100 -> max_connections,
  compute = ![max_connections]
}
```

### Обработка ошибок

Если в XML файле содержатся недопустимые структуры или ссылки на неизвестные константы, инструмент выдаст ошибку и предоставит полезное сообщение для выявления проблемы.

## Тестирование

Этот проект использует `pytest` для тестирования. Чтобы запустить тесты:

1. Установите `pytest`, если у вас его еще нет:

    ```bash
    pip install pytest
    ```

2. Запустите тесты:

    ```bash
    pytest test_converter.py
    ```

Вы увидите подобный вывод:

```bash
============================= test session starts =============================
collected 5 items

test_converter.py .....                                               [100%]

============================== 5 passed in 0.05s ==============================
```

## Примеры конфигураций

Ниже приведены примеры конфигураций XML из разных предметных областей, которые можно использовать с этим инструментом.

### Конфигурация веб-сервера

**Входной XML:**

```xml
<server port="8080">
  <host>localhost</host>
  <routes>
    <route path="/home" handler="homeHandler"/>
    <route path="/login" handler="loginHandler"/>
  </routes>
  <const name="MAX_CONNECTIONS" value="100"/>
  <compute name="MAX_CONNECTIONS"/>
</server>
```

**Конвертированный вывод:**

```plaintext
struct {
  port = 8080,
  host = "localhost",
  routes = struct {
    route = (list
      struct {
        path = "/home",
        handler = "homeHandler",
      }
      struct {
        path = "/login",
        handler = "loginHandler",
      }
    ),
  }
  100 -> maxconnections
  ![maxconnections]
}
```

### Конфигурация базы данных

**Входной XML:**

```xml
<database>
  <host>db.example.com</host>
  <port>5432</port>
  <user>dbuser</user>
  <password>dbpass</password>
  <tables>
    <table name="users"/>
    <table name="orders"/>
  </tables>
  <const name="TIMEOUT" value="30"/>
  <compute name="TIMEOUT"/>
</database>
```

**Конвертированный вывод:**

```plaintext
struct {
  host = "db.example.com",
  port = 5432,
  user = "dbuser",
  password = "dbpass",
  tables = struct {
    table = (list
      struct {
        name = "users",
      }
      struct {
        name = "orders",
      }
    ),
  }
  30 -> timeout
  ![timeout]
}
```

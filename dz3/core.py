#!/usr/bin/env python3
"""
XML to Configuration Language Converter

This script reads an XML file and converts it into a configuration language
with a specific syntax. The configuration language supports various constructs
like comments, arrays, dictionaries, constants, and more.

Usage:
    python converter.py -f input.xml

"""

import argparse
import sys
import re
import xml.etree.ElementTree as ET

def convert_element(element, indent=0, constants=None):
    """
    Рекурсивно преобразует XML-элемент в представление на языке конфигурации.

    Параметры:
        element (xml.etree.ElementTree.Element): Элемент XML для преобразования.
        indent (int): Текущий уровень отступа.
        constants (dict): Словарь для хранения констант.

    Возвращает:
        str: Представление элемента в языке конфигурации.
    """
    if constants is None:
        constants = {}

    indent_str = '  ' * indent  # Отступ на текущем уровне
    items = []

    # Обработка объявления констант
    if element.tag == 'const':
        name = element.get('name')
        value = element.get('value')
        if name and value:
            sanitized_name = sanitize_name(name)
            constants[sanitized_name] = value
            result = f"{indent_str}{convert_value(value)} -> {sanitized_name}"
            return result
        else:
            raise ValueError(f"Const element должен иметь атрибуты 'name' и 'value'.")

    # Обработка вычисления констант
    elif element.tag == 'compute':
        name = element.get('name')
        if name:
            sanitized_name = sanitize_name(name)
            if sanitized_name in constants:
                result = f"{indent_str}![{sanitized_name}]"
                return result
            else:
                raise ValueError(f"Константа '{sanitized_name}' не найдена.")
        else:
            raise ValueError(f"Элемент 'compute' должен иметь атрибут 'name'.")

    else:
        # Открывающая скобка структуры с правильным отступом
        result = indent_str + "struct {\n"

        # Обработка атрибутов элемента
        for attr_name, attr_value in element.attrib.items():
            name = sanitize_name(attr_name)
            value = convert_value(attr_value)
            items.append(f"{indent_str}  {name} = {value},")

        # Обработка дочерних элементов
        children = list(element)
        if children:
            # Группировка дочерних элементов по тегам
            child_groups = {}
            for child in children:
                tag = sanitize_name(child.tag)
                if tag not in child_groups:
                    child_groups[tag] = []
                child_groups[tag].append(child)

            for tag, group in child_groups.items():
                if len(group) == 1:
                    # Обработка одного дочернего элемента
                    value = convert_element(group[0], indent + 1, constants)
                    items.append(f"{indent_str}  {tag} = {value},")
                else:
                    # Обработка списка (несколько элементов с одинаковыми тегами)
                    list_items = []
                    for elem in group:
                        item = convert_element(elem, indent + 2, constants)
                        list_items.append(item)
                    # Формирование списка
                    list_str = "(list\n" + '\n'.join(list_items) + f"\n{indent_str}  )"
                    items.append(f"{indent_str}  {tag} = {list_str},")
        else:
            # Обработка текста в элементе
            text = element.text.strip() if element.text else ''
            if text:
                value = convert_value(text)
                return value  # Если это просто текст, возвращаем его напрямую

        result += '\n'.join(items).rstrip(',')  # Убираем лишние запятые
        result += f"\n{indent_str}}}"  # Закрывающая скобка на уровне структуры
        return result


def sanitize_name(name):
    """
    Санирует имя для использования в конфигурации.

    Параметры:
        name (str): Исходное имя.

    Возвращает:
        str: Очищенное имя, содержащее только строчные буквы.
    """
    return re.sub(r'[^a-zA-Z0-9]', '_', name.lower())

def convert_value(value):
    """
    Преобразует значение в конфигурацию.

    Параметры:
        value (str): Значение для преобразования.

    Возвращает:
        str: Преобразованное значение.
    """
    value = value.strip()
    if is_number(value):
        return value
    else:
        return f'"{value}"'
    

def post_process_config(config_str):
    """
    Постобработка строки конфигурации для удаления лишних пробелов перед `struct`
    и после знака "=" в выражениях.

    Параметры:
        config_str (str): Строка конфигурации.

    Возвращает:
        str: Обработанная строка.
    """
    # Убираем лишние пробелы перед struct, если перед ней стоит знак =
    config_str = re.sub(r'=\s+struct', '= struct', config_str)

    # Убираем лишние пробелы после знака = (делаем один пробел)
    config_str = re.sub(r'=\s+', '= ', config_str)

    return config_str


def is_number(s):
    """
    Проверяет, является ли строка числом.

    Параметры:
        s (str): Строка для проверки.

    Возвращает:
        bool: True, если строка — это число, иначе False.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def main():
    """
    Main function that parses command-line arguments and initiates the conversion process.
    """
    parser = argparse.ArgumentParser(description='XML to Configuration Language Converter')
    parser.add_argument('-f', '--file', required=True, help='Path to input XML file')
    args = parser.parse_args()

    try:
        tree = ET.parse(args.file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        config_str = convert_element(root)

        # Выполняем постобработку
        processed_config_str = post_process_config(config_str)

        # Выводим результат
        print(processed_config_str)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

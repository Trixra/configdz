from sys import argv
from os.path import exists
from graphviz import Digraph
from subprocess import call

import os
import zlib


def read_git_object(repo_path, object_hash):
    """Читает и распаковывает git-объект из папки .git/objects."""
    object_path = os.path.join(repo_path, ".git", "objects", object_hash[:2], object_hash[2:])
    with open(object_path, "rb") as f:
        compressed_content = f.read()
    content = zlib.decompress(compressed_content)
    return content


def parse_tree(repo_path, tree_hash, file_hash):
    """Рекурсивно обходит дерево и проверяет наличие нужного хеша файла."""
    content = read_git_object(repo_path, tree_hash)
    _, tree_content = content.split(b'\x00', 1)

    index = 0
    while index < len(tree_content):
        # Извлекаем метаданные (тип, права, хеш) для каждого объекта в дереве
        mode_end = tree_content.find(b' ', index)
        mode = tree_content[index:mode_end]

        name_end = tree_content.find(b'\x00', mode_end)
        name = tree_content[mode_end + 1:name_end]

        obj_hash = tree_content[name_end + 1:name_end + 21]
        obj_hash_hex = obj_hash.hex()

        # Проверка: если это искомый хеш, возвращаем True
        if obj_hash_hex.startswith(file_hash):
            return True

        # Если объект — дерево, обходим его рекурсивно
        if mode == b'40000':  # '40000' указывает на поддерево
            if parse_tree(repo_path, obj_hash_hex, file_hash):
                return True

        # Переходим к следующему объекту
        index = name_end + 21

    return False


def find_commits_with_hash(repo_path, file_hash):
    """Находит все коммиты с сообщениями, где указанный хеш файла присутствует в дереве."""
    git_objects_path = os.path.join(repo_path, ".git", "objects")
    commits_found = []

    for root, dirs, files in os.walk(git_objects_path):
        for file in files:
            object_hash = root[-2:] + file
            try:
                content = read_git_object(repo_path, object_hash)

                # Проверяем, является ли объект коммитом
                if content.startswith(b"commit"):
                    _, commit_content = content.split(b'\x00', 1)
                    commit_lines = commit_content.split(b'\n')

                    commit_message = b'\n'.join(commit_lines[commit_lines.index(b'') + 1:]).decode(errors="ignore")

                    if commit_message:
                        # Находим дерево, связанное с коммитом
                        tree_line = next(line for line in commit_lines if line.startswith(b"tree"))
                        tree_hash = tree_line.split()[1].decode()

                        # Проверяем дерево на наличие нужного хеша
                        if parse_tree(repo_path, tree_hash, file_hash):
                            commits_found.append((object_hash, commit_message))


            except Exception as e:
                print(f"Ошибка при чтении объекта {object_hash}: {e}")

    return commits_found


def build_commit_graph(repo_path, commits):
    """Создаёт код графа транзитивных зависимостей для списка коммитов."""

    graph = Digraph(comment='Commit Dependency Graph')

    for commit in commits:
        commit_hash, message = commit

        # Добавляем основной коммит
        graph.node(commit_hash, label=message)

        # Список для обработки коммитов
        commits_to_process = [commit_hash]

        while commits_to_process:
            current_commit = commits_to_process.pop()

            # Читаем объект коммита
            try:
                content = read_git_object(repo_path, current_commit)
                if content.startswith(b"commit"):
                    _, commit_content = content.split(b'\x00', 1)
                    commit_lines = commit_content.split(b'\n')

                    commit_message = b'\n'.join(commit_lines[commit_lines.index(b'') + 1:]).decode(errors="ignore")

                    # Извлекаем родителей
                    parent_hashes = [line.split()[1].decode() for line in commit_lines if line.startswith(b"parent")]

                    # Добавляем ребра для родителей
                    for parent in parent_hashes:
                        graph.node(parent, label=commit_message)  # Добавляем родителя в граф
                        graph.edge(current_commit, parent)  # Создаем ребро от текущего коммита к родителю
                        commits_to_process.append(parent)  # Добавляем родителя в очередь для дальнейшей обработки

            except Exception as e:
                print(f"Ошибка при чтении объекта {current_commit}: {e}")

    graph.body = list(set(graph.body))

    return graph.source


def build_graph(program, code):
    """Сохраняет код графа в текстовый файл и строит изображение графа"""
    name = 'my_graph.dot'
    with open(name, 'wt') as f:
        f.write(code)
    call([program, '-Tpng', name, '-O'])


def main():
    if len(argv) >= 4:
        program = argv[1]
        repo_path = argv[2]
        file_hash = argv[3]
    else:
        print('Введены не все ключи для корректного запуска')
        return

    if not exists(repo_path):
        print("Не все файлы по указанным путям существуют")
        return

    # Получаем все подходящие коммиты
    commits = find_commits_with_hash(repo_path, file_hash)
    # Получаем код графа зависимостей коммитов
    source = build_commit_graph(repo_path, commits)
    # Строим изображение графа коммитов
    build_graph(program, source)


if __name__ == '__main__':
    main()

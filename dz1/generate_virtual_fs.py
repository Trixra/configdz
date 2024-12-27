import os
import zipfile

# Создание структуры файловой системы
def create_virtual_fs_structure(base_dir):
    os.makedirs(os.path.join(base_dir, 'folder1'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'folder2'), exist_ok=True)

    # Создание файлов в folder1
    with open(os.path.join(base_dir, 'folder1', 'file1.txt'), 'w') as f:
        f.write('This is file1 in folder1.')
    with open(os.path.join(base_dir, 'folder1', 'file2.txt'), 'w') as f:
        f.write('This is file2 in folder1.')

    # Создание файлов в folder2
    with open(os.path.join(base_dir, 'folder2', 'file3.txt'), 'w') as f:
        f.write('This is file3 in folder2.')
    with open(os.path.join(base_dir, 'folder2', 'file4.txt'), 'w') as f:
        f.write('This is file4 in folder2.')

    # Создание startup.sh
    with open(os.path.join(base_dir, 'startup.sh'), 'w') as f:
        f.write('# startup.sh\n')
        f.write('echo "Running startup script..."\n')
        f.write('ls\n')
        f.write('cd folder1\n')
        f.write('ls\n')
        f.write('date\n')

# Создание ZIP-архива
def create_zip_archive(base_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, base_dir))

# Генерация виртуальной файловой системы
virtual_fs_dir = 'virtual_fs'
zip_file = 'virtual_fs.zip'

create_virtual_fs_structure(virtual_fs_dir)
create_zip_archive(virtual_fs_dir, zip_file)

# Удаление временной директории (для чистоты)
import shutil
shutil.rmtree(virtual_fs_dir)

print(f"ZIP archive {zip_file} generated successfully.")


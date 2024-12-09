import tkinter as tk
from tkinter import scrolledtext
import tarfile
import os

class Emulator:
    def __init__(self, root, username, tar_path, start_script=None):
        self.root = root
        self.username = username
        self.tar_path = tar_path
        self.current_dir = ''  # Начальная директория (пустая для "корневой")
        self.file_system = self.load_tar()

        self.root.title("Shell Emulator")
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.bind("<Return>", self.execute_command)
        self.text_area.focus()

        self.prompt()

        if start_script:
            self.execute_commands_from_file('start_script.txt')

    def load_tar(self):
        if not os.path.exists(self.tar_path):
            self.text_area.insert(tk.END, f"File not found: {self.tar_path}\n")
            return []

        with tarfile.open(self.tar_path, 'r') as tar:
            return [f for f in tar.getnames() if f.startswith(self.current_dir)]

    def remove_directory(self, directory):
        full_path = self.current_dir.rstrip('/') + directory.strip() + '/'
        self.text_area.insert(tk.END, f"Trying to remove: {full_path}\n")  # Отладочное сообщение

        # Выводим текущее состояние файловой системы
        self.file_system = self.load_tar()  # Обновляем содержимое перед удалением
        self.text_area.insert(tk.END, f"Current file system: {self.file_system}\n")

        # Проверяем, существует ли директория
        if full_path in self.file_system:
            # Удаляем директорию
            self.file_system.remove(full_path)
            self.text_area.insert(tk.END, f"Removed directory: {directory}\n")
            # Сохраняем изменения в tar файле
            self.save_tar()
        else:
            self.text_area.insert(tk.END, f"No such directory: {full_path}\n")

    def save_tar(self):
        with tarfile.open(self.tar_path, 'w') as tar:
            for f in self.file_system:
                tar.add(f, arcname=f[len(self.current_dir):])

    def prompt(self):
        self.text_area.insert(tk.END, f"\n{self.username}@emulator:{self.current_dir}~$ ")
        self.text_area.see(tk.END)

    def execute_command(self, event):
        input_text = self.text_area.get("end-1c linestart", "end-1c").strip()
        self.text_area.insert(tk.END, '\n')  # Move to next line
        command = input_text.split()
        if command:
            cmd = command[0]
            if cmd == 'exit':
                self.root.quit()
            elif cmd == 'ls':
                self.list_files()
            elif cmd == 'cd':
                if len(command) > 1:
                    self.change_directory(command[1])
                else:
                    self.text_area.insert(tk.END, "cd requires an argument\n")
            elif cmd == 'rmdir':
                if len(command) > 1:
                    self.remove_directory(command[1])
                else:
                    self.text_area.insert(tk.END, "rmdir requires an argument\n")
            elif cmd == 'wc':
                if len(command) > 1:
                    self.word_count(command[1])
                else:
                    self.text_area.insert(tk.END, "wc requires an argument\n")
            elif cmd == 'find':
                if len(command) > 1:
                    self.find_file(command[1])
                else:
                    self.text_area.insert(tk.END, "find requires an argument\n")
            else:
                self.text_area.insert(tk.END, f"Unknown command: {cmd}\n")
        self.prompt()


    def list_files(self):
        current_files = [f for f in self.file_system if f.startswith(self.current_dir)]
        if current_files:
            for file in current_files:
                self.text_area.insert(tk.END, f"{file[len(self.current_dir):]}  \n")
        else:
            self.text_area.insert(tk.END, "No files found\n")

    def change_directory(self, directory):
        if directory == '/':
            self.current_dir = ''
            self.text_area.insert(tk.END, f"Changed directory to: {self.current_dir}\n")
        elif directory == '..':
            self.current_dir = '/'.join(self.current_dir.split('/')[:-1]) + '/' if self.current_dir != '' else ''
            self.text_area.insert(tk.END, f"Changed directory to: {self.current_dir}\n")
        else:
            full_path = self.current_dir + directory
            if full_path in self.file_system:
                self.current_dir = full_path + '/'
                self.text_area.insert(tk.END, f"Changed directory to: {self.current_dir}\n")
            else:
                self.text_area.insert(tk.END, f"No such directory: {directory}\n")

    def remove_directory(self, directory):
        # Формируем полный путь к директории
        full_path = self.current_dir.rstrip('/') + '/' + directory.strip() + '/'

        # Сообщаем, что удаление невозможно
        self.text_area.insert(tk.END, f"Cannot remove directory {full_path}: This is a tar archive.\n")

    def word_count(self, filename):
        # Формируем полный путь к файлу
        full_path = self.current_dir + filename

        # Проверяем, существует ли файл в файловой системе
        if filename in self.file_system or full_path in self.file_system:
            # Если проверить full_path, а не filename
            file_to_check = full_path if full_path in self.file_system else filename

            with tarfile.open(self.tar_path, 'r') as tar:
                try:
                    member = tar.getmember(file_to_check)
                    if member.isfile():  # Проверяем, что это файл
                        f = tar.extractfile(member)
                        content = f.read().decode('utf-8')  # Читаем содержимое файла
                        total_words = len(content.split())
                        self.text_area.insert(tk.END, f"{file_to_check}: {total_words} words\n")
                    else:
                        self.text_area.insert(tk.END, f"No such file: {filename}\n")
                except KeyError:
                    self.text_area.insert(tk.END, f"No such file: {filename}\n")
        else:
            self.text_area.insert(tk.END, f"No such file: {filename}\n")

    def find_file(self, filename):
        full_path = self.current_dir + filename # текущая директория + имя файла
        if filename in self.file_system: # Проверяет, есть ли просто имя файла в файловой системе
            self.text_area.insert(tk.END, f"Found file: {self.current_dir}{filename}\n")
        elif full_path in self.file_system: # Если имя файла не найдено, проверяет наличие полного пути к файлу
            self.text_area.insert(tk.END, f"Found file: {full_path}\n")
        else:
            self.text_area.insert(tk.END, f"No such file: {filename}\n")

    def execute_commands_from_file(self, filename):
        if not os.path.exists(filename):
            self.text_area.insert(tk.END, f"File not found: {filename}\n")
            return

        with open(filename, 'r') as file:
            for line in file:
                command = line.strip()
                if command:
                    self.text_area.insert(tk.END, f"\nExecuting: {command}\n")
                    input_text = command.strip()
                    command_parts = input_text.split()
                    self.execute_command_from_list(command_parts)


    def execute_command_from_list(self, command_parts):
        if command_parts:
            cmd = command_parts[0]
            if cmd == 'cd':
                if len(command_parts) > 1:
                    self.change_directory(command_parts[1])
            elif cmd == 'wc':
                if len(command_parts) > 1:
                    self.word_count(command_parts[1])
            elif cmd == 'ls':
                self.list_files()
            elif cmd == 'find':
                if len(command_parts) > 1:
                    self.find_file(command_parts[1])


if __name__ == "__main__":
    root = tk.Tk()
    emulator = Emulator(root, "arina",
                        "C:\\Users\\arina\\PycharmProjects\\configupr\\tar.tar", "start_script.txt")
    root.mainloop()

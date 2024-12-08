import unittest
import tkinter as tk
from main import Emulator


class TestEmulator(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.text_area = tk.Text(self.root)  # Создаем текстовую область
        self.text_area.pack()  # Добавляем текстовую область в окно
        self.emulator = Emulator(self.root, "arina", "C:\\Users\\arina\\PycharmProjects\\configupr\\tar.tar")
        self.emulator.text_area = self.text_area  # Заменяем text_area на полноценный виджет

    def test_cd_1(self):
        self.emulator.current_dir = "tar/"
        self.emulator.change_directory("3")
        self.assertIn("Changed directory to: tar/3/", self.text_area.get("1.0", tk.END))

    def test_cd_2(self):
        self.text_area.delete("1.0", tk.END)
        self.emulator.change_directory("non_existing_dir")
        self.assertIn("No such directory: non_existing_dir", self.text_area.get("1.0", tk.END))

    def test_cd_3(self):
        self.emulator.current_dir = "tar/3/"
        self.text_area.delete("1.0", tk.END)
        self.emulator.change_directory("..")
        self.assertIn("Changed directory to: tar/", self.text_area.get("1.0", tk.END))

    def test_exit(self):
        self.emulator.execute_command(None)  # вызываем команду выхода
        self.assertTrue(self.root.winfo_exists())  # проверяем, открыто ли окно

    def test_find_1(self):
        self.emulator.file_system.append('tar/1/file1.txt')  # Добавляйте файл с полным путем
        self.emulator.current_dir = 'tar/1/'  # Установите текущую директорию так, чтобы файл был найден
        self.emulator.find_file('file1.txt')
        output = self.text_area.get("1.0", tk.END).strip()
        self.assertIn("Found file: file1.txt", output)

    def test_find_2(self):
        self.text_area.delete("1.0", tk.END)
        self.emulator.find_file('non_existing_file.txt')
        output = self.text_area.get("1.0", tk.END).strip()
        self.assertIn("No such file: non_existing_file.txt", output)

    def test_find_3(self):
        self.text_area.delete("1.0", tk.END)
        self.emulator.find_file('wrong name')
        output = self.text_area.get("1.0", tk.END).strip()
        self.assertIn("No such file: ", output)

    def test_wc_1(self):
        self.emulator.file_system.append('tar/2/file2.txt')
        self.emulator.current_dir = 'tar/2/'  # Установите текущую директорию перед вызовом метода
        self.emulator.word_count('file2.txt')
        output = self.text_area.get("1.0", tk.END).strip()
        self.assertIn("file2.txt:", output)  # Убедитесь, что  двоеточие присутствует

    def test_wc_2(self):
        self.text_area.delete("1.0", tk.END)
        self.emulator.word_count('non_existing_file.txt')
        output = self.text_area.get("1.0", tk.END).strip()
        self.assertIn("No such file: non_existing_file.txt", output)

    def test_wc_3(self):
        self.text_area.delete("1.0", tk.END)
        self.emulator.word_count('')
        output = self.text_area.get("1.0", tk.END).strip()
        self.assertIn("No such file:",
                      output)  # Убедитесь, что часть строки присутствует, не обращая внимания на пробелы

    def test_ls_1(self):
        self.emulator.file_system = ['tar/1/file1.txt', 'tar/2/file2.txt']
        self.emulator.list_files()
        output = self.text_area.get("1.0", tk.END)
        self.assertIn('file1.txt', output)
        self.assertIn('file2.txt', output)

    def test_ls_2(self):
        self.text_area.delete("1.0", tk.END)
        self.emulator.file_system = []
        self.emulator.list_files()
        self.assertIn("No files found", self.text_area.get("1.0", tk.END))

        self.text_area.delete("1.0", tk.END)
        self.emulator.current_dir = 'tar/'
        self.emulator.list_files()
        self.assertIn('No files found', self.text_area.get("1.0", tk.END))

    def test_rmdir(self):
        self.text_area.delete("1.0", tk.END)
        self.emulator.remove_directory('3')
        self.assertIn("Cannot remove directory ", self.text_area.get("1.0", tk.END))


if __name__ == "__main__":
    unittest.main()

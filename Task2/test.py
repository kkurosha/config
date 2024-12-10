import unittest
import os
from unittest.mock import patch, MagicMock
from main import DependencyVisualizer  # импортируйте ваш класс из правильного модуля


class TestDependencyVisualizer(unittest.TestCase):
    @patch("main.subprocess.run")  # замените visualize на main
    def test_get_commit_dependencies(self, mock_run):
        mock_run.return_value.stdout = "commit1 commit0\ncommit2 commit1"
        visualizer = DependencyVisualizer("config.yaml")
        dependencies = visualizer.get_commit_dependencies()
        self.assertEqual(dependencies, [("commit1", ["commit0"]), ("commit2", ["commit1"])])

    @patch("main.subprocess.run")  # замените visualize на main
    def test_get_commit_message(self, mock_run):
        mock_run.return_value.stdout = "Test commit message"
        visualizer = DependencyVisualizer("config.yaml")
        message = visualizer.get_commit_message("commit1")
        self.assertEqual(message, "Test commit message")

    def test_validate_config(self):
        visualizer = DependencyVisualizer("config.yaml")
        with self.assertRaises(FileNotFoundError):
            visualizer.graphviz_path = "/invalid/path"
            visualizer.validate_config()

    def test_build_graph(self):
        visualizer = DependencyVisualizer("config.yaml")
        with patch.object(visualizer, "get_commit_dependencies", return_value=[("commit1", ["commit0"])]):
            with patch.object(visualizer, "get_commit_message", return_value="Message"):
                graph = visualizer.build_graph()
                self.assertIn("commit1", graph.source)


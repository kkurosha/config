import yaml
import subprocess
from graphviz import Digraph
import os
import sys


class DependencyVisualizer:
    def __init__(self, config_path):
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        self.graphviz_path = config.get("graphviz_path")
        self.repo_path = config.get("repo_path")
        self.output_path = config.get("output_path")

        self.validate_config()

    def validate_config(self):
        if not os.path.exists(self.repo_path):
            raise FileNotFoundError(f"Git repository not found at {self.repo_path}")
        if not os.path.isdir(self.repo_path) or not os.path.exists(os.path.join(self.repo_path, ".git")):
            raise ValueError(f"{self.repo_path} is not a valid Git repository")
        if not os.path.exists(self.graphviz_path):
            raise FileNotFoundError(f"Graphviz tool not found at {self.graphviz_path}")

    def get_commit_dependencies(self):
        """
        Получает коммиты и их зависимости (родительские коммиты) из git-репозитория.
        """
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "log", "--pretty=format:%H %P"],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run git command: {e}")

        dependencies = []
        for line in result.stdout.splitlines():
            parts = line.split()
            commit = parts[0]
            parents = parts[1:]  # Если несколько родителей, они будут добавлены в список
            dependencies.append((commit, parents))

        print(f"Dependencies: {dependencies}")  # Отладка зависимостей
        return dependencies

    def build_graph(self):
        """
        Создает объект графа зависимости на основе данных из git.
        """
        dependencies = self.get_commit_dependencies()
        graph = Digraph()

        for commit, parents in dependencies:
            commit_msg = self.get_commit_message(commit)
            graph.node(commit, commit_msg)

            # Добавляем несколько рёбер, если у коммита несколько родителей
            for parent in parents:
                graph.edge(parent, commit)

        return graph

    def get_commit_message(self, commit):
        """
        Возвращает сообщение коммита.
        """
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "log", "-1", "--pretty=%B", commit],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to retrieve commit message for {commit}: {e}")

    def visualize(self):
        """
        Создает граф и сохраняет его в указанный файл.
        """
        graph = self.build_graph()  # Генерируем граф на основе коммитов и зависимостей
        print(f"Saving graph to {self.output_path}.png...")  # Сообщаем в консоль, что граф сохраняется
        graph.render(filename=self.output_path, format="png", engine="dot",
                     cleanup=True)  # Сохраняем граф в формате PNG
        print(f"Dependency graph successfully saved to {self.output_path}.png")  # Подтверждаем успешное сохранение


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_path>")
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        visualizer = DependencyVisualizer(config_path)
        visualizer.visualize()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

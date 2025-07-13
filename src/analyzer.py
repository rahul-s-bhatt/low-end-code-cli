# File: src/analyzer.py
from pathlib import Path
from collections import defaultdict, Counter
from tree_sitter_languages import get_parser
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from tree_sitter import Language, Parser

# Supported file extensions
EXT_LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cs": "c_sharp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".lua": "lua",
}

# Language support
LANG_NODE_TYPES = {
    "python": {
        "functions": ["function_definition"],
        "classes": ["class_definition"]
    },
    "javascript": {
        "functions": ["function"],
        "classes": ["class"]
    },
    # extend as needed...
}

class FileAnalyzer:
    """Analyzes a single file using tree-sitter to extract function/class names."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.lang = EXT_LANGUAGE_MAP.get(self.file_path.suffix, None)

    def analyze(self):
        result = {"language": self.lang, "functions": [], "classes": []}
        if not self.lang:
            return result

        try:
            parser = get_parser(self.lang)
            tree = parser.parse(bytes(self.file_path.read_text(), "utf8"))
            root = tree.root_node

            lang_nodes = LANG_NODE_TYPES.get(self.lang, {})
            func_types = lang_nodes.get("functions", [])
            class_types = lang_nodes.get("classes", [])

            for node in root.walk():
                try:
                    if node.type in func_types:
                        result["functions"].append(node.text.decode(errors="ignore"))
                    elif node.type in class_types:
                        result["classes"].append(node.text.decode(errors="ignore"))
                except:
                    continue

        except Exception as e:
            result["error"] = str(e)

        return result



class StructureAnalyzer:
    """Tracks semantic folder structure and language mix."""

    def __init__(self):
        self.structure = defaultdict(lambda: Counter())

    def add_file(self, file_path, lang):
        parts = Path(file_path).parts
        for i in range(1, len(parts)):
            folder = Path(*parts[:i])
            self.structure[str(folder)]["files"] += 1
            if lang:
                self.structure[str(folder)][lang] += 1

    def get_structure(self):
        return {k: dict(v) for k, v in self.structure.items()}



class ProjectAnalyzer:
    def __init__(self, root_path="."):
        self.root = Path(root_path)
        self.context_map = {}
        self.structure_analyzer = StructureAnalyzer()
        self.ignore_spec = self._load_gitignore()

    def _load_gitignore(self):
        gitignore_path = self.root / ".gitignore"
        if gitignore_path.exists():
            patterns = gitignore_path.read_text().splitlines()
        else:
            # fallback: use your default ignore list
            patterns = [
                ".venv/",
                "venv/",
                "__pycache__/",
                "*.pyc",
                "*.gguf",
                "*.bin",
                ".lec/",
                ".git/",
                "node_modules/",
            ]
        return PathSpec.from_lines(GitWildMatchPattern, patterns)

    def scan(self):
        for file in self.root.rglob("*"):
            rel_file = file.relative_to(self.root)

            if self.ignore_spec.match_file(str(rel_file)):
                continue

            if file.suffix in EXT_LANGUAGE_MAP:
                analyzer = FileAnalyzer(file)
                result = analyzer.analyze()
                self.context_map[str(file)] = result
                self.structure_analyzer.add_file(file, result.get("language"))

        self.context_map["__structure__"] = self.structure_analyzer.get_structure()
        return self.context_map
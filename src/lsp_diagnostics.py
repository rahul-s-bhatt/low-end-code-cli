# File: src/lsp_diagnostics.py
import subprocess
import json
from pathlib import Path

LSP_BACKENDS = {
    "python": "pyright",
    "typescript": "tsserver",
    "go": "gopls",
    "rust": "rust-analyzer",
    "c": "clangd",
    "cpp": "clangd",
    "java": "jdtls",
}

class LSPDiagnostics:
    def __init__(self, language: str = "python", root="."):
        self.language = language.lower()
        self.root = Path(root)

    def run(self, file=None):
        target = Path(file or self.root)
        if target.is_dir():
            py_files = list(target.rglob("*.py"))
            if not py_files:
                return [{
                    "file": str(target),
                    "line": None,
                    "message": "No Python files found in directory.",
                    "severity": "warning"
                }]
            return self._run_pyright_batch(py_files)
        else:
            return self._run_pyright(target)

    def _run_pyright_batch(self, file_list):
        diagnostics = []
        for f in file_list:
            diagnostics.extend(self._run_pyright(f))
        return diagnostics

    def _unsupported(self, tool):
        return [{
            "file": None,
            "line": None,
            "message": f"LSP backend '{tool}' not yet implemented",
            "severity": "info"
        }]

    def _run_pyright(self, target_file):
        target_file = target_file or self.root
        try:
            result = subprocess.run(
                ["pyright", "--outputjson", str(target_file)],
                capture_output=True, text=True, check=True
            )
            data = json.loads(result.stdout)
            return self._parse_pyright(data)
        except subprocess.CalledProcessError as e:
            return [{
                "file": str(target_file),
                "line": None,
                "message": f"Pyright error: {e.stderr.strip()}",
                "severity": "error"
            }]

    def _parse_pyright(self, data):
        diagnostics = []
        for diag in data.get("generalDiagnostics", []):
            diagnostics.append({
                "file": diag.get("file"),
                "line": diag.get("range", {}).get("start", {}).get("line", 0) + 1,
                "message": diag.get("message", ""),
                "severity": diag.get("severity", "info")
            })
        return diagnostics

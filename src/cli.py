# File: src/cli.py
import json
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from .model import LocalModel
from .context import FilesystemContext
from .analyzer import ProjectAnalyzer, EXT_LANGUAGE_MAP
from .project_metadata import ProjectMetadata
from pathlib import Path
from .smart_context import SmartContextBuilder
from .session_manager import SessionManager
from rich.table import Table
from .learn import LearnTracker
from .project_metadata import ProjectMetadata
from .lsp_diagnostics import LSPDiagnostics

console = Console()

@click.group()
def cli():
    """🚀 Low-End-Code: AI coding assistant for modest hardware"""
    pass

@cli.command()
def init():
    context = FilesystemContext()
    context.init_project()
    console.print(Panel("✅ Project initialized!", title="Success", style="green"))
    console.print(f"📁 Cache directory: {context.cache_dir}")

@cli.command()
@click.argument("path")
def select(path):
    console.print(f"🔍 Analyzing project at: {path}", style="blue")
    analyzer = ProjectAnalyzer(path)
    context_map = analyzer.scan()
    metadata_obj = ProjectMetadata(path)
    metadata = metadata_obj.generate_from_context(context_map)

    session_mgr = SessionManager()
    session_path = session_mgr.get_session_path(path)
    session_mgr.set_active(path)
    session_mgr.save_session_metadata(session_path, metadata)

    summary = f"""
                📁 Project: {Path(path).name}
                🧠 Files analyzed: {len(context_map)}
                💾 Session stored: {session_path}
                🔁 Session ID: {session_path.name}
                """
    console.print(Panel(summary.strip(), title="Session Activated", style="green"))

@cli.command()
@click.argument('path', default='.')
def init_metadata(path):
    analyzer = ProjectAnalyzer(path)
    context_map = analyzer.scan()
    metadata_obj = ProjectMetadata(path)
    meta = metadata_obj.generate_from_context(context_map)
    console.print(Panel("📄 PROJECT_METADATA.lec generated", title="Project Metadata", style="cyan"))
    console.print(meta)

@cli.command()
@click.argument('file')
def complete(file):
    try:
        console.print("🤖 Loading model...", style="blue")
        model = LocalModel()
        context_builder = FilesystemContext()

        console.print("📁 Building context...", style="yellow")
        context = context_builder.get_context(file)
        key = context_builder._generate_hash_key(context)
        cached = context_builder.load_cached_result(key)

        if cached:
            console.print("♻️ Using cached result", style="cyan")
            result = cached
        else:
            console.print("🧠 Generating completion...", style="magenta")
            result = model.complete_code(context)
            context_builder.cache_result(key, result)

        console.print(Panel(result, title="AI Completion", style="green"))

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")

@cli.command()
@click.argument('code')
def explain(code):
    try:
        console.print("🤖 Loading model...", style="blue")
        model = LocalModel()
        context_builder = FilesystemContext()
        key = context_builder._generate_hash_key(code)
        cached = context_builder.load_cached_result(key)

        if cached:
            console.print("♻️ Using cached result", style="cyan")
            result = cached
        else:
            console.print("📖 Generating explanation...", style="magenta")
            result = model.explain_code(code)
            context_builder.cache_result(key, result)

        console.print(Panel(result, title="Code Explanation", style="cyan"))

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")

@cli.command()
@click.argument('file')
def context(file):
    context_builder = FilesystemContext()
    builder = SmartContextBuilder()
    context = builder.build_for(file)
    lang = EXT_LANGUAGE_MAP.get(Path(file).suffix, "python")
    syntax = Syntax(context, lang, theme="monokai")
    console.print(Panel(syntax, title=f"Context for {file}", style="blue"))

@cli.group()
def sessions():
    """Manage project intelligence sessions"""
    pass

@sessions.command("list")
def list_sessions():
    mgr = SessionManager()
    active = mgr.get_active()
    console.print(f"\n🧠 [bold cyan]Active Session:[/] {active.name if active else 'None'}\n")
    for path in mgr.list_sessions():
        meta_path = path / "PROJECT_METADATA.lec"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            name = meta.get("project_name", "unknown")
            lang = meta.get("language", "unknown")
            mods = meta.get("generated_summary", {}).get("modules", "?")
            console.print(
                f"[{path.name}]  {name}  |  {lang}  |  {mods} modules"
                + (" [ACTIVE]" if path == active else "")
            )
        else:
            console.print(f"[{path.name}] <no metadata>")

@sessions.command("activate")
@click.argument("session_id")
def activate_session(session_id):
    mgr = SessionManager()
    target = mgr.sessions_dir / session_id
    if not target.exists():
        console.print(f"❌ No session found with ID: {session_id}", style="red")
        return
    mgr.active_path.write_text(str(target))
    console.print(f"✅ Activated session: {session_id}", style="green")

@sessions.command("delete")
@click.argument("session_id")
def delete_session(session_id):
    mgr = SessionManager()
    target = mgr.sessions_dir / session_id
    if not target.exists():
        console.print(f"❌ No session found with ID: {session_id}", style="red")
        return
    import shutil
    shutil.rmtree(target)
    console.print(f"🗑️ Deleted session: {session_id}", style="yellow")

@sessions.command("purge")
@click.confirmation_option(prompt="Are you sure you want to delete ALL sessions?")
def purge_sessions():
    mgr = SessionManager()
    import shutil
    shutil.rmtree(mgr.sessions_dir)
    mgr.sessions_dir.mkdir()
    console.print("🔥 All sessions purged.", style="red")

@cli.command()
def dashboard():
    mgr = SessionManager()
    session = mgr.get_active()
    if not session:
        console.print("❌ No active session found. Use 'lec select <path>' first.", style="red")
        return

    meta = mgr.load_session_metadata(session)
    if not meta:
        console.print("⚠️ No metadata found for active session.", style="yellow")
        return

    stats = meta.get("generated_summary", {})
    suggestions = [
        "🧩 Consider adding type hints to all public functions.",
        "🧪 Detected test folder, but some modules have no tests.",
        "📦 Project uses Flask but lacks request validation.",
    ]

    console.print(Panel(f"""📂 Project: {meta.get('project_name')}
🔁 Session ID: {session.name}
📦 Language: {meta.get('language')}
🧱 Modules: {stats.get('modules')} | 🧮 Functions: {stats.get('functions')} | 🧬 Classes: {stats.get('classes')}""", title="Active Project", style="cyan"))

    table = Table(title="💡 Suggestions", show_lines=True)
    table.add_column("#")
    table.add_column("Tip")
    for i, s in enumerate(suggestions, 1):
        table.add_row(str(i), s)

    console.print(table)

@cli.command()
@click.argument("source", type=click.Choice(["completion", "correction", "test"]))
@click.option("--file", help="Optional file to read content from")
def learn(source, file):
    """Manually log learnings from a source"""
    tracker = LearnTracker()
    if source == "completion":
        prompt = click.prompt("Prompt")
        result = click.prompt("Model response")
        accepted = click.confirm("Was this accepted?")
        tracker.log_completion(prompt, result, accepted)
    elif source == "correction":
        before = click.prompt("Before")
        after = click.prompt("After")
        reason = click.prompt("Why did you correct it?", default="")
        tracker.log_correction(before, after, reason)
    elif source == "test":
        file = file or click.prompt("Test file")
        passed = click.confirm("Did the test pass?")
        tracker.log_test_feedback(file, passed)
    console.print("✅ Learning logged.", style="green")

@cli.command()
@click.argument("file", default=".")
@click.option("--lang", default="python", help="Language to use for LSP (default: python)")
def lsp_diagnostics(file, lang):
    """Run LSP diagnostics on a file or directory"""
    console.print(f"🔍 Running diagnostics for: {file} [lang={lang}]", style="blue")

    diag = LSPDiagnostics(language=lang)
    issues = diag.run(file)

    if not issues:
        console.print("✅ No issues found", style="green")
    elif all("Pyright error" in i["message"] for i in issues):
        console.print("⚠️ Pyright had trouble analyzing. Try specifying a single file:", style="yellow")
        console.print("   lec lsp-diagnostics src/main.py", style="dim")
    else:
        for i in issues:
            file_str = f"{i['file']}:{i['line']}" if i['file'] else "(unknown)"
            console.print(f"🚨 {file_str} [{i['severity'].upper()}] {i['message']}", style="red")

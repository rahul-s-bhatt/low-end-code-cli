# File: src/cli.py
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from .model import LocalModel
from .context import FilesystemContext

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
    context = context_builder.get_context(file)
    syntax = Syntax(context, "python", theme="monokai")
    console.print(Panel(syntax, title=f"Context for {file}", style="blue"))

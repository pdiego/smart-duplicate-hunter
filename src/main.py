#!/usr/bin/env python3
"""
SmartDuplicateHunter - Herramienta inteligente para detectar archivos duplicados
"""

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

@click.command()
@click.version_option(version="1.0.0")
def main():
    """SmartDuplicateHunter - Detecta archivos duplicados de forma inteligente"""
    
    console.print(Panel.fit(
        "[bold blue]SmartDuplicateHunter v1.0.0[/bold blue]\n"
        "[green]Herramienta inteligente para detectar archivos duplicados[/green]",
        border_style="blue"
    ))
    
    console.print("\n[yellow]🔍 Iniciando análisis...[/yellow]")

if __name__ == "__main__":
    main()
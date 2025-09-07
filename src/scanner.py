#!/usr/bin/env python3
"""
SmartDuplicateHunter - Scanner Module
Módulo para escanear y filtrar archivos en directorios
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
from tqdm import tqdm
import yaml


@dataclass
class ScanConfig:
    """Configuración para el escaneo de archivos"""
    include_extensions: Set[str]
    exclude_directories: Set[str]
    min_file_size: int
    max_file_size: int
    follow_symlinks: bool = False
    ignore_hidden: bool = True


@dataclass
class FileInfo:
    """Información de un archivo encontrado"""
    path: Path
    size: int
    modified_time: float
    extension: str


class FileScanner:
    """Scanner inteligente de archivos con filtros y agrupación por tamaño"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar el scanner con configuración
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        self.config = self._load_config(config_path)
        self.files_by_size: Dict[int, List[FileInfo]] = defaultdict(list)
        self.total_files_found = 0
        self.total_size_scanned = 0
        
    def _load_config(self, config_path: Optional[str]) -> ScanConfig:
        """Cargar configuración desde archivo YAML o usar defaults"""
        default_config = {
            'scanning': {
                'include_extensions': [
                    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
                    '.mp3', '.wav', '.flac', '.aac', '.ogg',
                    '.pdf', '.doc', '.docx', '.txt', '.rtf',
                    '.zip', '.rar', '.7z', '.tar', '.gz'
                ],
                'exclude_directories': [
                    '__pycache__', '.git', '.svn', 'node_modules',
                    '.vscode', '.idea', 'venv', 'env',
                    'System Volume Information', '$RECYCLE.BIN'
                ],
                'min_file_size': 1024,  # 1KB
                'max_file_size': 10737418240,  # 10GB
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    # Merge con configuración default
                    scanning_config = {**default_config['scanning'], **user_config.get('scanning', {})}
            except Exception as e:
                print(f"⚠️  Error cargando configuración: {e}")
                scanning_config = default_config['scanning']
        else:
            scanning_config = default_config['scanning']
        
        return ScanConfig(
            include_extensions=set(ext.lower() for ext in scanning_config['include_extensions']),
            exclude_directories=set(scanning_config['exclude_directories']),
            min_file_size=scanning_config['min_file_size'],
            max_file_size=scanning_config['max_file_size']
        )
    
    def _should_include_file(self, file_path: Path) -> bool:
        """
        Determinar si un archivo debe incluirse en el análisis
        
        Args:
            file_path: Ruta del archivo a evaluar
            
        Returns:
            True si el archivo debe incluirse
        """
        # Verificar extensión
        if self.config.include_extensions and file_path.suffix.lower() not in self.config.include_extensions:
            return False
        
        # Ignorar archivos ocultos si está configurado
        if self.config.ignore_hidden and file_path.name.startswith('.'):
            return False
        
        try:
            # Verificar tamaño
            size = file_path.stat().st_size
            if size < self.config.min_file_size or size > self.config.max_file_size:
                return False
            
            # Verificar que no sea un archivo de tamaño 0
            if size == 0:
                return False
                
        except (OSError, FileNotFoundError):
            # No se puede acceder al archivo
            return False
        
        return True
    
    def _should_include_directory(self, dir_path: Path) -> bool:
        """
        Determinar si un directorio debe explorarse
        
        Args:
            dir_path: Ruta del directorio a evaluar
            
        Returns:
            True si el directorio debe explorarse
        """
        # Verificar si está en la lista de exclusión
        if dir_path.name in self.config.exclude_directories:
            return False
        
        # Ignorar directorios ocultos si está configurado
        if self.config.ignore_hidden and dir_path.name.startswith('.'):
            return False
        
        return True
    
    def scan_directory(self, directory: str, show_progress: bool = True) -> Dict[int, List[FileInfo]]:
        """
        Escanear un directorio y retornar archivos agrupados por tamaño
        
        Args:
            directory: Ruta del directorio a escanear
            show_progress: Mostrar barra de progreso
            
        Returns:
            Diccionario con archivos agrupados por tamaño
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"El directorio no existe: {directory}")
        
        if not directory_path.is_dir():
            raise NotADirectoryError(f"La ruta no es un directorio: {directory}")
        
        print(f"🔍 Escaneando: {directory_path.absolute()}")
        print(f"📋 Filtros: extensiones={len(self.config.include_extensions)}, "
              f"tamaño={self._format_size(self.config.min_file_size)}-{self._format_size(self.config.max_file_size)}")
        
        # Resetear contadores
        self.files_by_size.clear()
        self.total_files_found = 0
        self.total_size_scanned = 0
        
        # Primera pasada: contar archivos para la barra de progreso
        if show_progress:
            print("📊 Analizando estructura de directorios...")
            total_files = self._count_files(directory_path)
            pbar = tqdm(total=total_files, desc="Escaneando archivos", unit="archivos")
        
        # Segunda pasada: procesar archivos
        try:
            self._scan_recursive(directory_path, pbar if show_progress else None)
        finally:
            if show_progress:
                pbar.close()
        
        # Mostrar estadísticas
        self._print_scan_statistics()
        
        return dict(self.files_by_size)
    
    def _count_files(self, directory_path: Path) -> int:
        """Contar archivos totales para la barra de progreso"""
        count = 0
        try:
            for item in directory_path.rglob('*'):
                if item.is_file():
                    count += 1
        except (PermissionError, OSError):
            pass
        return count
    
    def _scan_recursive(self, directory_path: Path, pbar=None):
        """Escanear recursivamente un directorio"""
        try:
            for item in directory_path.iterdir():
                if item.is_file():
                    if pbar:
                        pbar.update(1)
                    
                    if self._should_include_file(item):
                        self._process_file(item)
                        
                elif item.is_dir() and self._should_include_directory(item):
                    # Recursión en subdirectorios
                    self._scan_recursive(item, pbar)
                    
        except (PermissionError, OSError) as e:
            print(f"⚠️  No se puede acceder a: {directory_path} - {e}")
    
    def _process_file(self, file_path: Path):
        """Procesar un archivo individual y agregarlo a la agrupación por tamaño"""
        try:
            stat = file_path.stat()
            file_info = FileInfo(
                path=file_path,
                size=stat.st_size,
                modified_time=stat.st_mtime,
                extension=file_path.suffix.lower()
            )
            
            # Agrupar por tamaño
            self.files_by_size[file_info.size].append(file_info)
            self.total_files_found += 1
            self.total_size_scanned += file_info.size
            
        except (OSError, FileNotFoundError) as e:
            print(f"⚠️  Error procesando {file_path}: {e}")
    
    def get_potential_duplicates(self) -> Dict[int, List[FileInfo]]:
        """
        Obtener solo grupos con más de un archivo (potenciales duplicados)
        
        Returns:
            Diccionario con solo grupos que tienen 2+ archivos del mismo tamaño
        """
        return {size: files for size, files in self.files_by_size.items() if len(files) > 1}
    
    def _print_scan_statistics(self):
        """Imprimir estadísticas del escaneo"""
        potential_duplicates = self.get_potential_duplicates()
        total_potential_files = sum(len(files) for files in potential_duplicates.values())
        total_potential_size = sum(size * len(files) for size, files in potential_duplicates.items())
        
        print(f"\n📊 Estadísticas del escaneo:")
        print(f"   📁 Archivos encontrados: {self.total_files_found:,}")
        print(f"   💾 Tamaño total: {self._format_size(self.total_size_scanned)}")
        print(f"   🔍 Grupos de mismo tamaño: {len(potential_duplicates):,}")
        print(f"   ⚡ Archivos candidatos: {total_potential_files:,}")
        print(f"   💰 Tamaño de candidatos: {self._format_size(total_potential_size)}")
        
        if potential_duplicates:
            # Mostrar los 5 grupos más grandes
            print(f"\n🔝 Top 5 grupos por cantidad:")
            sorted_groups = sorted(potential_duplicates.items(), key=lambda x: len(x[1]), reverse=True)
            for i, (size, files) in enumerate(sorted_groups[:5], 1):
                print(f"   {i}. {len(files)} archivos de {self._format_size(size)} cada uno")
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Formatear tamaño en bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


def demo_scan():
    """Función de demostración del scanner"""
    import tempfile
    import os
    
    # Crear archivos de prueba
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Crear algunos archivos de prueba
        (temp_path / "test1.txt").write_text("Hello World!")
        (temp_path / "test2.txt").write_text("Hello World!")  # Duplicado
        (temp_path / "test3.txt").write_text("Different content")
        (temp_path / "image.jpg").write_bytes(b"fake_image_data")
        
        # Crear subdirectorio
        subdir = temp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("Nested file")
        
        print("🧪 Ejecutando demo del scanner...")
        scanner = FileScanner()
        results = scanner.scan_directory(str(temp_path))
        
        print(f"\n✅ Demo completada. Grupos encontrados: {len(results)}")


if __name__ == "__main__":
    demo_scan()
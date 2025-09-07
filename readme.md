# SmartDuplicateHunter

**Herramienta inteligente para detectar y gestionar archivos duplicados**

## ✨ Características

- 🎯 **Detección exacta** - Encuentra duplicados idénticos con precisión
- 🖼️ **Similitud en imágenes** - Detecta imágenes similares con diferentes resoluciones/compresión
- 🎵 **Análisis de medios** - Compara metadatos de audio y video
- ⚡ **Alto rendimiento** - Procesamiento paralelo y hashing optimizado
- 🛡️ **Gestión segura** - Envío a papelera y opciones de recuperación
- 📊 **Reportes detallados** - Análisis completo con estadísticas

## 🚀 Instalación rápida


git clone <repository-url>
cd smart-duplicate-hunter
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

Recorrer las carpetas elegidas.
Ignorar extensiones/carpetas excluidas, archivos de sistema, tamaños 0 si no interesan.
Agrupar candidatos por tamaño (si no coinciden en tamaño, no pueden ser iguales).
Para cada grupo de igual tamaño, calcular un hash del archivo (MD5/SHA-1/BLAKE3/xxHash).
Muchas apps hacen hash parcial (p. ej., primeros y últimos N KB) para acelerar y después pasan a hash completo solo para los que coinciden.
Para evitar falsos positivos por colisiones, comparar byte-a-byte solo entre archivos con el mismo hash.
Imágenes: usar perceptual hashing (aHash/dHash/pHash); dos fotos con distinta compresión/escala pueden dar hashes “cercanos”.
Música/Vídeo: comparar metadatos (título, artista, duración) y/o fingerprints (p. ej., Chromaprint en música).
Definir un umbral de similitud


Bibliotecas especializadas disponibles:
* hashlib (MD5, SHA-1, BLAKE3) para hashing
* PIL/Pillow + imagehash para perceptual hashing de imágenes
* mutagen para metadatos de audio/video
* send2trash para envío seguro a papelera
* pathlib para manejo moderno de rut
* concurrent.futures para paralelización

```
smart-duplicate-hunter/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── scanner.py
│   ├── hasher.py
│   ├── similarity.py
│   ├── analyzer.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_scanner.py
├── docs/
├── requirements.txt
├── README.md
├── .gitignore
└── config.yaml
```

## USO

# Análisis básico
```
python src/main.py scan /ruta/a/analizar
```

# Con opciones avanzadas
```
python src/main.py scan /ruta/a/analizar --similarity --auto-clean
```









### Scanner.py

🎯 Características del Scanner:
Funcionalidades principales:

✅ Escaneo recursivo con filtros inteligentes
✅ Agrupación por tamaño (optimización clave)
✅ Configuración flexible vía YAML
✅ Barra de progreso con tqdm
✅ Estadísticas detalladas
✅ Manejo de errores robusto

Filtros incluidos:

📁 Exclusión de directorios (.git, node_modules, etc.)
📄 Filtro por extensiones
📏 Filtro por tamaño (min/max)
👁️ Ignorar archivos ocultos
🚫 Evitar archivos de tamaño 0

🧪 Prueba el scanner:
Guarda el código en src/scanner.py y ejecuta:
```
python src/scanner.py
```
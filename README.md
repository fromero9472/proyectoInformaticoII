# Buscador académico (Tkinter + ttkbootstrap)

## Descripción
Aplicación de escritorio para búsqueda rápida en un `data.json`. Interfaz con `ttkbootstrap`, resaltado de términos y tarjetas con scroll interno.

## Estructura del proyecto
```
PythonProject/
├─ src/
│  ├─ gui.py        # interfaz y arranque
│  └─ search.py     # lógica de normalización, tokenización y ranking
└─ data/
   └─ data.json     # base de conocimiento
```

## Requisitos
- Python 3.10+ (incluye Tkinter en Windows/macOS; en Linux instalar `tk` del sistema).
- Paquetes Python:
  - `ttkbootstrap`
  - `Pillow` (dependencia de ttkbootstrap)

Instalación de dependencias:
```bash
python -m pip install --upgrade pip
python -m pip install ttkbootstrap Pillow
```

En Linux, si falta Tk:
- Debian/Ubuntu: `sudo apt install python3-tk`
- Fedora: `sudo dnf install python3-tkinter`
- Arch: `sudo pacman -S tk`

## Ejecución
Forma recomendada (como módulo, asegura imports):
```bash
python -m src.gui
```

Alternativa (ejecutar archivo directamente; ya está preparado para ambos):
```bash
python src/gui.py
```

En PowerShell con venv bloqueado por políticas, puedes ejecutar sin activar:
```powershell
& C:\ruta\al\proyecto\.venv\Scripts\python.exe -m src.gui
```

## Uso
- Escribe términos en “Buscar”.
- Elige modo: Tema / Palabras / Ambos.
- Resultados ordenados por relevancia.
- Cada tarjeta muestra el contenido completo; si excede el alto visible, aparece scroll dentro de la tarjeta.

## Formato de `data/data.json`
Lista de objetos con:
- `tema` (str)
- `palabras_clave` (lista[str])
- `contenido` (str)

Ejemplo:
```json
{
  "tema": "Tipos de Cable de Conexión",
  "palabras_clave": ["unipolar", "bipolar", "coaxial"],
  "contenido": "Texto explicativo..."
}
```

## Solución de problemas
- ImportError “attempted relative import…”:
  - Ejecuta como módulo: `python -m src.gui`.
- No aparece la GUI / error de Tk:
  - Instala Tkinter del sistema (ver Requisitos).
- PowerShell bloquea activar venv:
  - Ejecuta sin activar (ver Ejecución) o usa: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

## Personalización rápida
- Tema visual: en `src/gui.py`, `tb.Window(themename="flatly")` (otros temas: `darkly`, `minty`, `pulse`, etc.).
- Alto del área de lectura por tarjeta: `height=8` en `src/gui.py` (ajústalo a tu preferencia).



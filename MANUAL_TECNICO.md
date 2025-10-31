# Manual técnico — Buscador académico

## Resumen del sistema
Aplicación de escritorio (Windows/Linux/macOS) que permite buscar contenidos educativos dentro de un archivo `data.json`.  
Ofrece interfaz moderna con `ttkbootstrap`, búsqueda en vivo, ranking de resultados y tarjetas con resaltado y scroll interno.

---

## Tecnologías utilizadas y justificación
- **Python 3.10+**: lenguaje accesible, multiplataforma y con biblioteca estándar amplia. Ideal para contexto escolar.  
- **Tkinter**: GUI nativa incluida con Python; sin dependencias pesadas.  
- **ttkbootstrap**: estilos modernos sobre Tkinter para apariencia actual sin necesidad de CSS/HTML.  
- **unicodedata**: normalización y remoción de acentos para coincidencias insensibles a acentos.  
- **re**: coincidencias simples para resaltado, pero reemplazado en la búsqueda principal por comparación directa (más rápida).  
- **functools.lru_cache**: almacenamiento temporal de resultados para acelerar consultas repetidas.  
- **pathlib**: manejo portable de rutas.  
- **json**: almacenamiento simple y legible para el corpus del proyecto.  
- *(opcional)* **PyInstaller**: empaquetado en `.exe` para PCs sin Python instalado.

---

## Decisiones de diseño
- Aplicación **offline**, sin necesidad de conexión a Internet.  
- Datos en `data/data.json`: estructura liviana y editable.  
- Separación por capas:
  - `src/search.py`: lógica de búsqueda.
  - `src/gui.py`: interfaz gráfica.
- Normalización de texto en minúsculas sin acentos.  
- Ranking interpretable: prioridad a `tema`, luego `palabras_clave` y finalmente `contenido`.  
- Scroll interno en tarjetas para mostrar texto completo.  
- Debounce en la entrada para evitar búsquedas excesivas.

---

## Optimización de rendimiento (nueva versión `search.py`)
Se implementaron varias mejoras manteniendo compatibilidad total con la interfaz:

### 🔹 Preprocesamiento de artículos
Al cargar los datos, cada artículo se normaliza una sola vez (`tema_norm`, `kws_norm`, `contenido_norm`), evitando recalcular en cada búsqueda.  
Esto reduce drásticamente el tiempo por consulta.

### 🔹 Eliminación de expresiones regulares costosas
Las coincidencias en contenido se realizan ahora mediante operaciones de substring simples (`in`), mucho más rápidas que los patrones `re.search` previos.

### 🔹 Cacheo de resultados (`lru_cache`)
Consultas repetidas (por ejemplo, al tipear letra por letra) se obtienen instantáneamente sin volver a recorrer todos los artículos.

### 🔹 Complejidad mejorada
Antes: O(N × regex)  
Ahora: O(N × comparación directa), con normalización precalculada.

---

## Arquitectura y módulos

### `src/search.py`
Funciones y responsabilidades:
- `normalize_text(text)`: remueve acentos, pasa a minúsculas.  
- `tokenize(text)`: divide texto en tokens normalizados.  
- `preprocess_articles(articles)`: agrega campos normalizados.  
- `score_article(article, q_tokens, mode)`: calcula puntuaciones sin usar regex pesado.  
- `_cached_search_all(query, mode, key)`: motor interno con cache.  
- `load_dataset(articles)`: inicializa dataset y limpia cache.  
- `search_all(articles, query, mode)`: interfaz pública compatible con la GUI.

### `src/gui.py`
Sin cambios funcionales. Sigue usando:
- `load_articles()` para cargar `data.json`.  
- `App`: clase principal de la interfaz con debounce, búsqueda y renderizado de resultados.

---

## Flujo de ejecución
1. Cargar artículos desde `data/data.json`.  
2. Preprocesamiento de normalización (una sola vez).  
3. El usuario escribe y selecciona el modo de búsqueda (tema/palabras/ambos).  
4. `search_all()` obtiene resultados ordenados (usando cache si aplica).  
5. Se renderizan tarjetas con resaltado del texto.

---

## Rendimiento y límites
- Conjunto actual: búsqueda prácticamente instantánea.  
- Escalable hasta miles de artículos sin bloqueos.  
- Para volúmenes mayores, puede migrarse a indexado con SQLite FTS5 o Whoosh.

---

## Portabilidad
- Funciona en Python 3.10+ (Windows/macOS/Linux).  
- Si se empaqueta con PyInstaller, no requiere instalación previa de Python.

---

## Seguridad y privacidad
- Datos 100 % locales, sin conexión externa.  
- Manejo de errores al cargar JSON con mensaje informativo al usuario.

---

## Extensiones futuras
- Ejecución en hilo separado (búsqueda asíncrona).  
- Filtros avanzados y exportación de resultados.  
- Stemming, sinónimos, y selector de tema claro/oscuro.  
- Pruebas unitarias automáticas (pytest).

---


import re
import unicodedata
from typing import List, Dict
from functools import lru_cache

# ==========================================================
# Configuración
# ==========================================================
MAX_FRAGMENT = 240  # compatibilidad
MIN_QUERY_LEN = 2   # ignorar búsquedas muy cortas


# ==========================================================
# Funciones básicas
# ==========================================================
def normalize_text(text: str) -> str:
    """Normaliza texto (acentos, mayúsculas, espacios)."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower().strip()


def tokenize(text: str) -> List[str]:
    """Convierte texto en lista de tokens normalizados."""
    norm = normalize_text(text)
    return [t for t in re.split(r"\W+", norm) if t]


# ==========================================================
# Preprocesamiento (mejora de rendimiento)
# ==========================================================
def preprocess_articles(articles: List[Dict]) -> List[Dict]:
    """Agrega versiones normalizadas a cada artículo."""
    for a in articles:
        a["tema_norm"] = normalize_text(a.get("tema", ""))
        a["kws_norm"] = [normalize_text(k) for k in a.get("palabras_clave", [])]
        a["contenido_norm"] = normalize_text(a.get("contenido", ""))
    return articles


# ==========================================================
# Búsqueda
# ==========================================================
def score_article(article: Dict, q_tokens: List[str], mode: str) -> List[Dict]:
    """Devuelve coincidencias con puntajes según el modo."""
    results: List[Dict] = []
    if not q_tokens:
        return results

    tema = article.get("tema", "")
    kws = [str(k) for k in article.get("palabras_clave", [])]
    contenido = article.get("contenido", "")

    tema_norm = article.get("tema_norm", "")
    kws_norm = article.get("kws_norm", [])
    contenido_norm = article.get("contenido_norm", "")

    # --- Tema ---
    if mode in ("tema", "ambos"):
        tema_hits = sum(1 for t in q_tokens if t in tema_norm)
        if tema_hits:
            results.append({
                "score": 40 + 4 * tema_hits,
                "origen": "tema",
                "tema": tema,
                "palabras_clave": kws,
                "fragmento": contenido,
            })

    # --- Palabras clave ---
    if mode in ("palabras", "ambos"):
        kw_matches = [(raw, sum(1 for t in q_tokens if t in norm))
                      for raw, norm in zip(kws, kws_norm)]
        kw_matches = [(raw, h) for raw, h in kw_matches if h > 0]
        if kw_matches:
            top_kw, top_hits = max(kw_matches, key=lambda x: x[1])
            results.append({
                "score": 28 + 3 * top_hits + min(len(kw_matches), 4),
                "origen": "palabras_clave",
                "tema": tema,
                "palabras_clave": kws,
                "coincidencia": top_kw,
                "fragmento": contenido,
            })

    # --- Contenido (sin regex costoso) ---
    if any(t in contenido_norm for t in q_tokens):
        results.append({
            "score": 18 + len(q_tokens),
            "origen": "contenido",
            "tema": tema,
            "palabras_clave": kws,
            "fragmento": contenido,
        })

    return results


# ==========================================================
# Cacheo de resultados
# ==========================================================
@lru_cache(maxsize=64)
def _cached_search_all(query: str, mode: str, key: int) -> List[Dict]:
    """Función cacheada para búsquedas repetidas."""
    # Nota: `key` sirve para invalidar cache si cambia el dataset.
    global _ARTICLES
    results = {}
    q_tokens = tokenize(query)

    for a in _ARTICLES:
        for r in score_article(a, q_tokens, mode):
            k = r.get("tema", "")
            if k not in results or r["score"] > results[k]["score"]:
                results[k] = r

    return sorted(results.values(), key=lambda r: r["score"], reverse=True)


# ==========================================================
# API pública
# ==========================================================
_ARTICLES: List[Dict] = []
_DATA_VERSION = 0  # incrementa si se recarga data


def load_dataset(articles: List[Dict]):
    """Prepara y almacena artículos para búsquedas rápidas."""
    global _ARTICLES, _DATA_VERSION
    _ARTICLES = preprocess_articles(articles)
    _DATA_VERSION += 1
    _cached_search_all.cache_clear()


def search_all(articles: List[Dict], query: str, mode: str) -> List[Dict]:
    """Interfaz pública compatible con el GUI."""
    if not query or len(query.strip()) < MIN_QUERY_LEN:
        return []

    # Si el dataset cambia, recargar cache
    global _ARTICLES
    if _ARTICLES != articles:
        load_dataset(articles)

    return _cached_search_all(query, mode, _DATA_VERSION)

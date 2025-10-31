import json
import sys
from pathlib import Path
from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# Permite ejecutar este archivo directamente (python src/gui.py) o como módulo (-m src.gui)
_SRC_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SRC_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from src.search import tokenize, search_all
except Exception:
    # Fallback para ejecución como paquete
    from .search import tokenize, search_all


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "data.json"
DEBOUNCE_MS = 250


def load_articles() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [data]
    if not isinstance(data, list):
        raise ValueError("El JSON debe ser lista de objetos o un objeto único.")
    return data


class App:
    def __init__(self, app: tb.Window, articles: list[dict]):
        self.app = app
        self.articles = articles
        self.after_id = None

        app.title("Buscador académico")
        app.geometry("940x640")
        app.minsize(820, 520)

        top = tb.Frame(app, padding=12)
        top.pack(side=TOP, fill=X)

        self.query_var = tb.StringVar()
        tb.Label(top, text="Buscar:", font=("Segoe UI", 11, "bold")).pack(side=LEFT)
        self.entry = tb.Entry(top, textvariable=self.query_var, width=40)
        self.entry.pack(side=LEFT, fill=X, expand=True, padx=8)

        self.mode_var = tb.StringVar(value="ambos")
        tb.Radiobutton(top, text="Tema", variable=self.mode_var, value="tema", bootstyle=PRIMARY).pack(side=LEFT, padx=(6, 0))
        tb.Radiobutton(top, text="Palabras", variable=self.mode_var, value="palabras", bootstyle=PRIMARY).pack(side=LEFT, padx=6)
        tb.Radiobutton(top, text="Ambos", variable=self.mode_var, value="ambos", bootstyle=PRIMARY).pack(side=LEFT, padx=6)

        self.btn = tb.Button(top, text="Buscar", bootstyle=SUCCESS, command=self.run_search)
        self.btn.pack(side=LEFT, padx=(10, 0))
        self.clear_btn = tb.Button(top, text="Limpiar", bootstyle=SECONDARY, command=self.clear_query)
        self.clear_btn.pack(side=LEFT, padx=6)

        self.scroll = ScrolledFrame(app, padding=12, autohide=True)
        self.scroll.pack(side=TOP, fill=BOTH, expand=True)
        self.container = tb.Frame(self.scroll)
        self.container.pack(fill=BOTH, expand=True)

        self.status = tb.Label(app, text="Escribe para buscar…", anchor="w", bootstyle=INFO)
        self.status.pack(side=BOTTOM, fill=X, padx=12, pady=6)

        self.entry.bind("<KeyRelease>", self.on_key_release)
        app.bind("<Return>", lambda *_: self.run_search())

        self.show_results(None)

    def clear_query(self):
        self.query_var.set("")
        self.show_results(None)

    def on_key_release(self, _e):
        if self.after_id is not None:
            self.app.after_cancel(self.after_id)
        self.after_id = self.app.after(DEBOUNCE_MS, self.run_search)

    def run_search(self):
        self.after_id = None
        q = self.query_var.get().strip()
        mode = self.mode_var.get()
        results = search_all(self.articles, q, mode)
        self.show_results(results, query=q)

    def show_results(self, results: list[dict] | None, query: str = ""):
        for w in self.container.winfo_children():
            w.destroy()

        if results is None:
            self.status.configure(text="Escribe para buscar…")
            return

        q_tokens = tokenize(query)

        if not results:
            card = self._card(self.container, "Sin resultados", "—", "No se encontraron coincidencias.")
            card.pack(fill=X, pady=6)
            self.status.configure(text="0 resultados")
            return

        for r in results:
            subtitle = f"{r['tema']} • {r['origen']}"
            desc = r.get("fragmento", "")
            card = self._card(
                self.container,
                title=r['tema'],
                subtitle=subtitle,
                body=desc,
                badges=r.get("palabras_clave", []),
                query_tokens=q_tokens,
            )
            card.pack(fill=X, pady=8)

        self.status.configure(text=f"{len(results)} resultados")

    def _card(self, parent, title: str, subtitle: str, body: str,
              badges: list[str] | None = None, query_tokens: list[str] | None = None):
        f = tb.Frame(parent, bootstyle="secondary", padding=12)
        f.configure(borderwidth=1)

        tb.Label(f, text=title, font=("Segoe UI Semibold", 12)).pack(anchor="w")
        tb.Label(f, text=subtitle, font=("Segoe UI", 9), bootstyle=SECONDARY).pack(anchor="w", pady=(2, 6))

        if badges:
            tagrow = tb.Frame(f)
            tagrow.pack(anchor="w", pady=(0, 6))
            for kw in badges[:10]:
                tb.Label(tagrow, text=kw, bootstyle=(INFO, "inverse"), padding=(6, 2)).pack(side=LEFT, padx=3)

        # Área de texto con scroll interno para leer todo el contenido
        text_row = tb.Frame(f)
        text_row.pack(fill=BOTH, expand=True)
        text = tb.Text(text_row, height=8, wrap="word")
        vsb = tb.Scrollbar(text_row, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=vsb.set)
        text.pack(side=LEFT, fill=BOTH, expand=True)
        # Scrollbar se mostrará solo si hay overflow; se decide más abajo
        text.insert("1.0", body)

        if query_tokens:
            for tok in sorted(set(query_tokens), key=len, reverse=True):
                if not tok:
                    continue
                start = "1.0"
                while True:
                    pos = text.search(tok, start, nocase=True, stopindex="end")
                    if not pos:
                        break
                    end = f"{pos}+{len(tok)}c"
                    text.tag_add("hl", pos, end)
                    start = end
            text.tag_config("hl", background="#fff3cd")

        text.configure(state="disabled")

        # Mostrar/ocultar scrollbar según fracción visible (rápido y ligero)
        def update_scrollbar(_e=None):
            first, last = text.yview()
            if last < 1.0:
                if not vsb.winfo_ismapped():
                    vsb.pack(side=RIGHT, fill=Y)
            else:
                if vsb.winfo_ismapped():
                    vsb.pack_forget()

        text.update_idletasks()
        update_scrollbar()
        text.bind("<Configure>", update_scrollbar)
        return f


def main():
    try:
        articles = load_articles()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar data.json\n{e}")
        return

    app = tb.Window(themename="flatly")
    App(app, articles)
    app.mainloop()


if __name__ == "__main__":
    main()



import json, hashlib, threading
from pathlib import Path
from typing import Any, Optional

class ResultCache:
    """Einfacher kombinierter RAM + Disk Cache für Analyse-Ergebnisse.
    Key = Hash aus Datei-Pfaden + mtime + size + Rule-Profile.
    """
    def __init__(self, base_dir: Optional[Path] = None, max_entries: int = 50):
        self.base = (base_dir or Path.home() / ".quality_app" / "cache")
        self.base.mkdir(parents=True, exist_ok=True)
        self._mem: dict[str, dict] = {}
        self._order: list[str] = []
        self._lock = threading.Lock()
        self.max = max_entries

    @staticmethod
    def make_key(files: dict, rule_profile: str = "default") -> str:
        h = hashlib.sha256()
        def _upd(s: str):
            try:
                h.update(s.encode("utf-8", "ignore"))
            except Exception:
                pass
        _upd(rule_profile)
        for k in ("source", "translation"):
            for p in files.get(k, []) or []:
                p = str(p)
                _upd(p)
                try:
                    stat = Path(p).stat()
                    _upd(str(stat.st_mtime_ns))
                    _upd(str(stat.st_size))
                except Exception:
                    _upd("NA")
        return h.hexdigest()

    def get(self, key: str) -> Optional[dict]:
        with self._lock:
            if key in self._mem:  # RAM hit
                try:
                    self._order.remove(key)
                except ValueError:
                    pass
                self._order.insert(0, key)
                return self._mem[key]
        fp = self.base / f"{key}.json"
        if fp.exists():
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                with self._lock:
                    self._mem[key] = data
                    if key in self._order:
                        try: self._order.remove(key)
                        except ValueError: pass
                    self._order.insert(0, key)
                    self._shrink()
                return data
            except Exception:
                return None
        return None

    def set_async(self, key: str, data: dict):
        def _w():
            try:
                (self.base / f"{key}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                with self._lock:
                    self._mem[key] = data
                    if key in self._order:
                        try: self._order.remove(key)
                        except ValueError: pass
                    self._order.insert(0, key)
                    self._shrink()
            except Exception:
                pass
        threading.Thread(target=_w, daemon=True).start()

    def _shrink(self):
        while len(self._order) > self.max:
            k = self._order.pop()
            self._mem.pop(k, None)

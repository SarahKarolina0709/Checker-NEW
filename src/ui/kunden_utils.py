"""
Lightweight KundenUtils shim to satisfy SmartUploadCalendar imports during integration.
This provides minimal helpers backed by existing app/customer data.
Follows Design System and No-Icons policy implicitly via calling app when needed.
"""
from __future__ import annotations
from typing import Dict, Any, Optional
import os

class KundenUtils:
    @staticmethod
    def load_customers_from_json(path: str) -> Dict[str, Dict[str, Any]]:
        try:
            import json
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                # Normalize to expected dict structure keyed by code or name
                if isinstance(raw, dict):
                    return raw
                if isinstance(raw, list):
                    result: Dict[str, Dict[str, Any]] = {}
                    for c in raw:
                        if isinstance(c, dict):
                            code = c.get('code') or c.get('name') or c.get('id') or ''
                            if code:
                                result[str(code)].update(c) if code in result else result.setdefault(str(code), c)
                    return result
            return {}
        except Exception:
            return {}

    @staticmethod
    def extract_date_from_folder(folder_name: str) -> Optional[str]:
        """Flexible Erkennung von Datumsordnern.

        Unterstützte Muster:
        - YYYY-MM-DD
        - YYYY-MM-DD_<suffix>
        - <prefix>_YYYY-MM-DD (letzte 10 Zeichen)
        - YYYYMMDD (kompakt) / YYYYMMDD_<suffix>
        - <prefix>_YYYYMMDD (letzte 8 Ziffern) → wird zu YYYY-MM-DD normalisiert
        """
        try:
            name = os.path.basename(folder_name).strip()
            # 1) Direkter ISO 10
            if len(name) >= 10 and name[4] == '-' and name[7] == '-':
                candidate = name[:10]
                if candidate[:4].isdigit() and candidate[5:7].isdigit() and candidate[8:10].isdigit():
                    return candidate
            # 2) Enthält Unterstrich nach ISO
            if '_' in name:
                parts = name.split('_')
                for part in parts:
                    if len(part) == 10 and part[4] == '-' and part[7] == '-' and part[:4].isdigit() and part[5:7].isdigit() and part[8:10].isdigit():
                        return part
            # 3) Kompakte 8-stellige Form (YYYYMMDD) in Segmenten
            def _expand(blk: str) -> Optional[str]:
                if len(blk) == 8 and blk.isdigit():
                    return f"{blk[0:4]}-{blk[4:6]}-{blk[6:8]}"
                return None
            if len(name) >= 8 and name[:8].isdigit() and len(name) >= 8:
                exp = _expand(name[:8])
                if exp:
                    return exp
            if '_' in name:
                for part in name.split('_'):
                    exp = _expand(part)
                    if exp:
                        return exp
            # 4) Letzte 10 oder 8 Zeichen (Suffix-Muster)
            if len(name) >= 10:
                tail10 = name[-10:]
                if tail10[4:5] == '-' and tail10[7:8] == '-' and tail10[:4].isdigit() and tail10[5:7].isdigit() and tail10[8:10].isdigit():
                    return tail10
            if len(name) >= 8:
                tail8 = name[-8:]
                exp = _expand(tail8)
                if exp:
                    return exp
            return None
        except Exception:
            return None

    @staticmethod
    def get_customer_display_name(customer_code: str, customers: Dict[str, Dict[str, Any]]) -> str:
        # Try exact key
        if customer_code in customers and isinstance(customers[customer_code], dict):
            return customers[customer_code].get('name') or customers[customer_code].get('display') or customer_code
        # Try case-insensitive match by code field
        try:
            code_lower = customer_code.lower()
            for key, data in customers.items():
                if not isinstance(data, dict):
                    continue
                if str(key).lower() == code_lower:
                    return data.get('name') or data.get('display') or customer_code
                if str(data.get('code', '')).lower() == code_lower:
                    return data.get('name') or data.get('display') or customer_code
        except Exception:
            pass
        return customer_code

    @staticmethod
    def format_project_display_name(folder_name: str) -> str:
        # Prefer folder name; optionally strip time suffix
        base = os.path.basename(folder_name)
        if '_' in base and len(base) >= 13:
            # Example: 2025-07-06_1430 -> 2025-07-06 14:30
            try:
                date, time = base.split('_', 1)
                if len(time) >= 4 and time[:4].isdigit():
                    return f"{date} {time[:2]}:{time[2:4]}"
            except Exception:
                return base
        return base

# Simple provider helpers used by SmartUploadCalendar
_singleton: Optional[KundenUtils] = None

def get_kunden_utils() -> KundenUtils:
    global _singleton
    if _singleton is None:
        _singleton = KundenUtils()
    return _singleton

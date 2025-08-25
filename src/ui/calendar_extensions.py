"""
Minimal CalendarExtensions shim to satisfy SmartUploadCalendar.
Provides lightweight statistics and export helpers; safe no-op fallbacks.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import csv

@dataclass
class CalendarStats:
    total_upload_days: int
    total_projects: int
    total_files: int
    customers_count: int
    average_files_per_project: float
    busiest_day: Optional[str]
    busiest_customer: Optional[str]
    month_name: str
    year: int

class CalendarExtensions:
    def __init__(self, app=None):
        self.app = app
        self._cache = {}

    def get_cached_statistics(self, month_data: Dict[str, List[dict]], current_date: datetime) -> CalendarStats:
        key = (current_date.year, current_date.month)
        if key in self._cache:
            return self._cache[key]
        stats = self._compute_statistics(month_data, current_date)
        self._cache[key] = stats
        return stats

    def _compute_statistics(self, month_data: Dict[str, List[dict]], current_date: datetime) -> CalendarStats:
        upload_days = len([1 for _ in month_data.keys()])
        total_projects = sum(len(v) for v in month_data.values())
        total_files = sum(p.get('file_count', 0) for v in month_data.values() for p in v)
        customers = {
            p.get('customer', '')
            for v in month_data.values()
            for p in v
            if p.get('customer')
        }
        avg = (total_files / total_projects) if total_projects else 0.0

        # busiest day by file count
        busiest_day = None
        max_files = -1
        for d, projects in month_data.items():
            files = sum(p.get('file_count', 0) for p in projects)
            if files > max_files:
                max_files = files
                busiest_day = d

        # busiest customer by total files
        cust_files = {}
        for projects in month_data.values():
            for p in projects:
                cust = p.get('customer', '')
                cust_files[cust] = cust_files.get(cust, 0) + p.get('file_count', 0)
        busiest_customer = max(cust_files, key=cust_files.get) if cust_files else None

        months = ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
                  "Juli", "August", "September", "Oktober", "November", "Dezember"]
        return CalendarStats(
            total_upload_days=upload_days,
            total_projects=total_projects,
            total_files=total_files,
            customers_count=len(customers),
            average_files_per_project=avg,
            busiest_day=busiest_day,
            busiest_customer=busiest_customer,
            month_name=months[current_date.month],
            year=current_date.year,
        )

    def export_to_csv(self, data: Dict[str, List[dict]], file_path: str, date_range: Optional[Tuple[datetime, datetime]] = None) -> bool:
        try:
            rows = []
            for date_str, projects in data.items():
                if date_range:
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d")
                        if not (date_range[0] <= dt <= date_range[1]):
                            continue
                    except Exception:
                        pass
                for p in projects:
                    rows.append([
                        date_str,
                        p.get('customer', ''),
                        p.get('customer_code', ''),
                        p.get('project_folder', ''),
                        p.get('file_count', 0)
                    ])
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Datum", "Kunde", "Code", "Projekt", "Dateien"])
                writer.writerows(rows)
            return True
        except Exception:
            return False

    def export_to_excel(self, data: Dict[str, List[dict]], file_path: str, date_range=None) -> bool:
        # Minimal shim: write CSV with .xlsx extension
        return self.export_to_csv(data, file_path, date_range)

    def export_to_pdf(self, data: Dict[str, List[dict]], file_path: str, date_range=None) -> bool:
        # Minimal shim: write CSV with .pdf extension (placeholder)
        return self.export_to_csv(data, file_path, date_range)

    def search_projects(self, data: Dict[str, List[dict]], term: str) -> Dict[str, List[dict]]:
        term_low = (term or "").lower()
        result = {}
        for d, projects in data.items():
            filtered = [p for p in projects if term_low in str(p).lower()]
            if filtered:
                result[d] = filtered
        return result

    def filter_by_customer(self, data: Dict[str, List[dict]], name: str) -> Dict[str, List[dict]]:
        term_low = (name or "").lower()
        result = {}
        for d, projects in data.items():
            filtered = [p for p in projects if term_low in str(p.get('customer', '')).lower()]
            if filtered:
                result[d] = filtered
        return result

    def get_yearly_overview(self, data: Dict[str, List[dict]], year: int) -> Dict:
        out = {}
        for d, projects in data.items():
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                if dt.year != year:
                    continue
                month = dt.strftime("%Y-%m")
                out.setdefault(month, 0)
                out[month] += sum(p.get('file_count', 0) for p in projects)
            except Exception:
                continue
        return out

    def preload_month_data(self, data: Dict[str, List[dict]], month_date: datetime):
        # No-op shim for preloading
        return

    def clear_cache(self):
        self._cache.clear()


def create_calendar_extensions(app=None) -> CalendarExtensions:
    return CalendarExtensions(app)

# -*- coding: utf-8 -*-
"""Tests fuer nicegui_app.customers."""
import os
import sys
import tempfile
import shutil
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nicegui_app import customers as C


# ---------------------------------------------------------------------------
# sanitize_folder_name
# ---------------------------------------------------------------------------
class TestSanitize:
    def test_basic(self):
        assert C.sanitize_folder_name('Maier GmbH') == 'Maier_GmbH'

    def test_path_traversal_blocked(self):
        assert '/' not in C.sanitize_folder_name('../etc/passwd')
        assert '\\' not in C.sanitize_folder_name(r'..\windows')

    def test_special_chars(self):
        assert C.sanitize_folder_name('A<>:"|?*B') == 'AB'

    def test_ampersand(self):
        assert C.sanitize_folder_name('A & B') == 'A_B'

    def test_empty(self):
        assert C.sanitize_folder_name('') == 'Unbenannt'

    def test_only_dots(self):
        assert C.sanitize_folder_name('...') == 'Unbenannt'

    def test_double_spaces(self):
        assert C.sanitize_folder_name('A    B') == 'A_B'


class TestDisplayName:
    def test_underscore_to_space(self):
        assert C.display_name('Finnland_GmbH') == 'Finnland GmbH'

    def test_empty(self):
        assert C.display_name('') == ''


# ---------------------------------------------------------------------------
# MONTH_FOLDER_RE — Regression Bug 44
# ---------------------------------------------------------------------------
class TestMonthFolderRegex:
    def test_valid_month(self):
        assert C.MONTH_FOLDER_RE.match('März_2025')
        assert C.MONTH_FOLDER_RE.match('Januar_2026')
        assert C.MONTH_FOLDER_RE.match('Dezember_1999')

    def test_customer_with_month_prefix_rejected(self):
        # Bug 44 regression: "Maier_GmbH" duerfte NICHT als Monat erkannt werden
        assert not C.MONTH_FOLDER_RE.match('Maier_GmbH')
        assert not C.MONTH_FOLDER_RE.match('Mai_GmbH')
        assert not C.MONTH_FOLDER_RE.match('Maerz_GmbH')

    def test_partial_match_rejected(self):
        assert not C.MONTH_FOLDER_RE.match('März_2025_extra')
        assert not C.MONTH_FOLDER_RE.match('März_25')


# ---------------------------------------------------------------------------
# find_source_folder / find_translation_folder
# ---------------------------------------------------------------------------
class TestFolderFinders:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_find_source_alias_german(self):
        os.makedirs(os.path.join(self.tmp, '01_Ausgangstext'))
        assert C.find_source_folder(self.tmp).endswith('01_Ausgangstext')

    def test_find_source_alias_english(self):
        os.makedirs(os.path.join(self.tmp, 'source'))
        assert C.find_source_folder(self.tmp).endswith('source')

    def test_find_source_missing(self):
        assert C.find_source_folder(self.tmp) == ''

    def test_find_source_empty_path(self):
        assert C.find_source_folder('') == ''

    def test_find_translation_umlaut(self):
        # Wichtig: Umlaut darf nicht verloren gehen
        os.makedirs(os.path.join(self.tmp, '02_Übersetzung'))
        assert C.find_translation_folder(self.tmp).endswith('02_Übersetzung')

    def test_find_translation_plural(self):
        os.makedirs(os.path.join(self.tmp, '02_Übersetzungen'))
        assert C.find_translation_folder(self.tmp).endswith('02_Übersetzungen')

    def test_find_translation_alt(self):
        os.makedirs(os.path.join(self.tmp, '03_Übersetzung'))
        assert C.find_translation_folder(self.tmp).endswith('03_Übersetzung')


# ---------------------------------------------------------------------------
# count_files / list_files
# ---------------------------------------------------------------------------
class TestFileCounters:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_count_ignores_subdirs_and_dotfiles(self):
        open(os.path.join(self.tmp, 'a.txt'), 'w').close()
        open(os.path.join(self.tmp, 'b.txt'), 'w').close()
        open(os.path.join(self.tmp, '.hidden'), 'w').close()
        os.makedirs(os.path.join(self.tmp, 'sub'))
        assert C.count_files_in_folder(self.tmp) == 2

    def test_count_missing_dir(self):
        assert C.count_files_in_folder('/nonexistent/path/xyz') == 0

    def test_list_sorted(self):
        open(os.path.join(self.tmp, 'b.txt'), 'w').close()
        open(os.path.join(self.tmp, 'a.txt'), 'w').close()
        result = C.list_files_in_folder(self.tmp)
        assert len(result) == 2
        assert result[0].endswith('a.txt')


# ---------------------------------------------------------------------------
# load_customers — Strukturen A/B/C
# ---------------------------------------------------------------------------
class TestLoadCustomers:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_empty_base(self):
        assert C.load_customers(self.tmp) == []

    def test_no_base(self):
        assert C.load_customers('') == []
        assert C.load_customers('/nonexistent/xyz') == []

    def test_variant_a_flat(self):
        os.makedirs(os.path.join(self.tmp, '2026-01-15_Kunde1'))
        os.makedirs(os.path.join(self.tmp, '2026-02-20_Kunde2'))
        assert C.load_customers(self.tmp) == ['Kunde1', 'Kunde2']

    def test_variant_b_month_nested(self):
        os.makedirs(os.path.join(self.tmp, 'Januar_2026', '2026-01-15_KundeB'))
        assert C.load_customers(self.tmp) == ['KundeB']

    def test_variant_c_old(self):
        os.makedirs(os.path.join(self.tmp, 'Maier_GmbH'))
        os.makedirs(os.path.join(self.tmp, 'Maier_GmbH', '2025-05-12'))
        assert C.load_customers(self.tmp) == ['Maier_GmbH']

    def test_ignores_archive_dir(self):
        os.makedirs(os.path.join(self.tmp, '_archiv'))
        os.makedirs(os.path.join(self.tmp, 'Kunde1'))
        assert C.load_customers(self.tmp) == ['Kunde1']

    def test_dedupe(self):
        # Kunde taucht in 2 Monaten auf
        os.makedirs(os.path.join(self.tmp, 'Januar_2026', '2026-01-15_Mehrfach'))
        os.makedirs(os.path.join(self.tmp, 'Februar_2026', '2026-02-20_Mehrfach'))
        assert C.load_customers(self.tmp) == ['Mehrfach']


# ---------------------------------------------------------------------------
# scan_project_dates
# ---------------------------------------------------------------------------
class TestScanProjectDates:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_variant_a(self):
        os.makedirs(os.path.join(self.tmp, '2026-04-23_Acme'))
        result = C.scan_project_dates(self.tmp)
        assert result == {'2026-04-23': ['Acme']}

    def test_variant_b(self):
        os.makedirs(os.path.join(self.tmp, 'April_2026', '2026-04-23_Acme'))
        result = C.scan_project_dates(self.tmp)
        assert result == {'2026-04-23': ['Acme']}

    def test_variant_c(self):
        os.makedirs(os.path.join(self.tmp, 'AltKunde', '2025-05-12'))
        result = C.scan_project_dates(self.tmp)
        assert result == {'2025-05-12': ['AltKunde']}

    def test_multiple_customers_same_day(self):
        os.makedirs(os.path.join(self.tmp, '2026-01-01_KundeA'))
        os.makedirs(os.path.join(self.tmp, '2026-01-01_KundeB'))
        result = C.scan_project_dates(self.tmp)
        assert result == {'2026-01-01': ['KundeA', 'KundeB']}


# ---------------------------------------------------------------------------
# list_projects(_full)
# ---------------------------------------------------------------------------
class TestListProjects:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_variant_a(self):
        os.makedirs(os.path.join(self.tmp, '2026-04-23_Acme'))
        assert C.list_projects(self.tmp, 'Acme') == ['2026-04-23_Acme']

    def test_variant_b(self):
        os.makedirs(os.path.join(self.tmp, 'April_2026', '2026-04-23_Acme'))
        os.makedirs(os.path.join(self.tmp, 'Mai_2026', '2026-05-12_Acme'))
        result = C.list_projects(self.tmp, 'Acme')
        # Sortierung absteigend (neueste zuerst)
        assert result == ['2026-05-12_Acme', '2026-04-23_Acme']

    def test_case_insensitive(self):
        os.makedirs(os.path.join(self.tmp, '2026-04-23_acme'))
        assert C.list_projects(self.tmp, 'Acme') == ['2026-04-23_acme']

    def test_full_returns_paths(self):
        os.makedirs(os.path.join(self.tmp, '2026-04-23_Acme'))
        result = C.list_projects_full(self.tmp, 'Acme')
        assert len(result) == 1
        assert result[0][0] == '2026-04-23_Acme'
        assert os.path.isdir(result[0][1])


# ---------------------------------------------------------------------------
# archive_customer
# ---------------------------------------------------------------------------
class TestArchive:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_archive_old_structure(self):
        os.makedirs(os.path.join(self.tmp, 'Kunde1', '2025-01-01'))
        assert C.archive_customer(self.tmp, 'Kunde1') is True
        assert not os.path.exists(os.path.join(self.tmp, 'Kunde1'))
        assert os.path.exists(os.path.join(self.tmp, '_archiv', 'Kunde1'))

    def test_archive_new_structure(self):
        os.makedirs(os.path.join(self.tmp, 'Januar_2026', '2026-01-15_KundeN'))
        assert C.archive_customer(self.tmp, 'KundeN') is True
        assert not os.path.exists(os.path.join(self.tmp, 'Januar_2026', '2026-01-15_KundeN'))
        assert os.path.exists(os.path.join(self.tmp, '_archiv', 'KundeN', 'Januar_2026', '2026-01-15_KundeN'))

    def test_archive_missing_returns_false(self):
        assert C.archive_customer(self.tmp, 'NichtDa') is False

    def test_archive_no_base(self):
        assert C.archive_customer('', 'Kunde') is False


# ---------------------------------------------------------------------------
# normalize_search + filter_customers
# ---------------------------------------------------------------------------
class TestNormalizeSearch:
    def test_lowercase_trim(self):
        assert C.normalize_search('  Acme GmbH  ') == 'acme gmbh'

    def test_umlauts(self):
        assert C.normalize_search('Müller') == 'mueller'
        assert C.normalize_search('Öko Größe') == 'oeko groesse'

    def test_underscore_to_space(self):
        assert C.normalize_search('Finnland_GmbH') == 'finnland gmbh'

    def test_collapse_whitespace(self):
        assert C.normalize_search('a   b') == 'a b'

    def test_empty(self):
        assert C.normalize_search('') == ''
        assert C.normalize_search(None) == ''


class TestFilterCustomers:
    def test_empty_query_returns_all_cleaned(self):
        names = ['Acme', 'Bravo_GmbH']
        assert C.filter_customers(names, '') == ['Acme', 'Bravo_GmbH']

    def test_skips_internal_folders(self):
        names = ['Acme', '_intern', '.hidden', '12345', 'Bravo']
        assert C.filter_customers(names, '') == ['Acme', 'Bravo']

    def test_substring_match(self):
        names = ['Alpha', 'Beta', 'Gamma']
        assert C.filter_customers(names, 'amm') == ['Gamma']

    def test_umlaut_tolerant(self):
        names = ['Müller', 'Meier']
        assert C.filter_customers(names, 'mueller') == ['Müller']
        assert C.filter_customers(names, 'müller') == ['Müller']

    def test_underscore_vs_space(self):
        # Ordnername hat _, User sucht mit Leerzeichen (Anzeigename)
        names = ['Finnland_GmbH']
        assert C.filter_customers(names, 'Finnland GmbH') == ['Finnland_GmbH']
        assert C.filter_customers(names, 'finnland gmbh') == ['Finnland_GmbH']

    def test_startswith_priority(self):
        names = ['XAlpha', 'AlphaCorp']
        # 'alpha' kommt in beiden vor; AlphaCorp startet damit -> zuerst
        assert C.filter_customers(names, 'alpha') == ['AlphaCorp', 'XAlpha']

    def test_limit(self):
        names = [f'Kunde{i}' for i in range(20)]
        assert len(C.filter_customers(names, '', limit=15)) == 15

    def test_no_match_returns_empty(self):
        assert C.filter_customers(['Acme'], 'zzz') == []

    def test_ignores_empty_names(self):
        assert C.filter_customers(['', 'Acme', None], '') == ['Acme']

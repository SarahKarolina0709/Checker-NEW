# -*- coding: utf-8 -*-
"""Tests fuer nicegui_app.session."""
import json
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nicegui_app import session as S


class TestGetSessionPath:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.fb = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.fb, ignore_errors=True)

    def test_uses_project_when_exists(self):
        assert S.get_session_path(self.tmp, self.fb) == os.path.join(self.tmp, 'session.json')

    def test_falls_back_when_project_missing(self):
        assert S.get_session_path('/nonexistent/xyz', self.fb) == os.path.join(self.fb, 'session.json')

    def test_falls_back_when_empty(self):
        assert S.get_session_path('', self.fb) == os.path.join(self.fb, 'session.json')


class TestBuildSessionData:
    def test_complete_state(self):
        state = {
            'source_files': ['a.pdf'],
            'translation_files': ['b.pdf'],
            'paired_results': [{'src': 'a', 'tgt': 'b'}],
            'findings': [{'kind': 'x'}],
            'checked_findings': {'0': True, '2': False},
            'active_customer': 'KundeX',
            'active_project_path': '/p/q',
            'current_score': 87,
        }
        d = S.build_session_data(state)
        assert d['customer'] == 'KundeX'
        assert d['project_path'] == '/p/q'
        assert d['score'] == 87
        assert d['source_files'] == ['a.pdf']
        assert d['checked_findings'] == {'0': True, '2': False}
        assert 'timestamp' in d

    def test_empty_state(self):
        d = S.build_session_data({})
        assert d['customer'] == ''
        assert d['score'] == -1
        assert d['source_files'] == []
        assert d['checked_findings'] == {}
        assert d['score_history'] == []
        assert d['manual_glossary_terms'] == {}
        assert d['glossary_path'] == ''


class TestSaveLoad:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_roundtrip(self):
        path = os.path.join(self.tmp, 'session.json')
        data = {'customer': 'X', 'score': 42, 'findings': []}
        assert S.save_session(path, data) is True
        loaded = S.load_session_from_path(path)
        assert loaded['customer'] == 'X'
        assert loaded['score'] == 42

    def test_atomic_no_tmp_left(self):
        path = os.path.join(self.tmp, 'session.json')
        S.save_session(path, {'a': 1})
        assert not os.path.exists(path + '.tmp')

    def test_save_creates_parent_dir(self):
        path = os.path.join(self.tmp, 'sub', 'dir', 'session.json')
        assert S.save_session(path, {'a': 1}) is True
        assert os.path.isfile(path)

    def test_load_missing_returns_none(self):
        assert S.load_session_from_path('/nonexistent/x.json') is None

    def test_load_empty_path_returns_none(self):
        assert S.load_session_from_path('') is None

    def test_load_corrupt_returns_none(self):
        path = os.path.join(self.tmp, 'session.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{not valid json')
        assert S.load_session_from_path(path) is None

    def test_atomic_overwrite_preserves_old_on_failure(self):
        # Bestehende valide Datei wird nicht korrumpiert wenn neue Daten geschrieben werden
        path = os.path.join(self.tmp, 'session.json')
        S.save_session(path, {'version': 1})
        S.save_session(path, {'version': 2})
        assert S.load_session_from_path(path)['version'] == 2


class TestFindLatest:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_base(self):
        assert S.find_latest_session('') == ''
        assert S.find_latest_session('/nonexistent/xyz') == ''

    def test_finds_latest(self):
        import time
        a = os.path.join(self.tmp, 'p1', 'session.json')
        b = os.path.join(self.tmp, 'p2', 'session.json')
        os.makedirs(os.path.dirname(a))
        os.makedirs(os.path.dirname(b))
        with open(a, 'w', encoding='utf-8') as f: json.dump({'x': 1}, f)
        time.sleep(0.05)
        with open(b, 'w', encoding='utf-8') as f: json.dump({'x': 2}, f)
        assert S.find_latest_session(self.tmp) == b

    def test_no_session_file(self):
        os.makedirs(os.path.join(self.tmp, 'sub'))
        assert S.find_latest_session(self.tmp) == ''


class TestLoadSession:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.fb = tempfile.mkdtemp()
        self.base = tempfile.mkdtemp()

    def teardown_method(self):
        for d in (self.tmp, self.fb, self.base):
            shutil.rmtree(d, ignore_errors=True)

    def test_prefers_active_project(self):
        with open(os.path.join(self.tmp, 'session.json'), 'w', encoding='utf-8') as f:
            json.dump({'src': 'project'}, f)
        with open(os.path.join(self.fb, 'session.json'), 'w', encoding='utf-8') as f:
            json.dump({'src': 'fallback'}, f)
        assert S.load_session(self.tmp, self.fb, self.base)['src'] == 'project'

    def test_uses_fallback_when_project_missing(self):
        with open(os.path.join(self.fb, 'session.json'), 'w', encoding='utf-8') as f:
            json.dump({'src': 'fallback'}, f)
        assert S.load_session('', self.fb, self.base)['src'] == 'fallback'

    def test_uses_latest_when_others_missing(self):
        sub = os.path.join(self.base, 'p1')
        os.makedirs(sub)
        with open(os.path.join(sub, 'session.json'), 'w', encoding='utf-8') as f:
            json.dump({'src': 'discovered'}, f)
        assert S.load_session('', self.fb, self.base)['src'] == 'discovered'

    def test_returns_none_when_nothing(self):
        assert S.load_session('', self.fb, self.base) is None

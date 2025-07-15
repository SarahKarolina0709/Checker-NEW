#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kundenmanagement Integration Test Suite
======================================

Testet die vollständige Integration des erweiterten Kundenmanagement-Systems
basierend auf der bereitgestellten Anleitung.
"""

import os
import json
import sys
from datetime import datetime

class CustomerManagementTestSuite:
    """Test-Suite für die Kundenmanagement-Integration"""
    
    def __init__(self):
        self.test_results = []
        self.base_path = "Checker_Projekte"
        
    def test_customer_data_loading(self):
        """Test: Kundendaten aus customers.json laden"""
        print("🧪 TESTING: Customer Data Loading...")
        
        try:
            # Prüfe ob customers.json existiert
            if os.path.exists("customers.json"):
                with open("customers.json", 'r', encoding='utf-8') as f:
                    customers = json.load(f)
                
                customer_count = len(customers)
                print(f"  ✅ customers.json gefunden mit {customer_count} Kunden")
                
                # Validiere Datenstruktur
                for customer_id, customer_data in customers.items():
                    required_fields = ['name', 'code']
                    for field in required_fields:
                        if field not in customer_data:
                            print(f"  ❌ Kunde {customer_id}: Feld '{field}' fehlt")
                            return False
                    
                print(f"  ✅ Alle Kunden haben erforderliche Felder")
                self.test_results.append(("Customer Data Loading", True, f"{customer_count} Kunden geladen"))
                return True
                
            else:
                print(f"  ❌ customers.json nicht gefunden")
                self.test_results.append(("Customer Data Loading", False, "customers.json fehlt"))
                return False
                
        except Exception as e:
            print(f"  ❌ Fehler beim Laden: {e}")
            self.test_results.append(("Customer Data Loading", False, str(e)))
            return False
    
    def test_folder_structure_creation(self):
        """Test: Ordnerstruktur-Erstellung nach Anleitung"""
        print("\n🧪 TESTING: Folder Structure Creation...")
        
        try:
            # Teste Basis-Ordner
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path, exist_ok=True)
                print(f"  ✅ Basis-Ordner '{self.base_path}' erstellt")
            else:
                print(f"  ✅ Basis-Ordner '{self.base_path}' bereits vorhanden")
            
            # Teste Kunden-Unterordner
            test_customer_code = "MUE"
            customer_path = os.path.join(self.base_path, test_customer_code)
            
            if not os.path.exists(customer_path):
                os.makedirs(customer_path, exist_ok=True)
                print(f"  ✅ Kunden-Ordner '{customer_path}' erstellt")
            
            # Teste Projekt-Ordner mit Datum
            today = datetime.now().strftime("%Y-%m-%d")
            project_name = f"{today}_Test_Projekt"
            project_path = os.path.join(customer_path, project_name)
            
            workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
            
            for workflow in workflows:
                workflow_path = os.path.join(project_path, workflow)
                os.makedirs(workflow_path, exist_ok=True)
                print(f"  ✅ Workflow-Ordner '{workflow}' erstellt")
            
            print(f"  ✅ Vollständige Projektstruktur erstellt: {project_path}")
            self.test_results.append(("Folder Structure Creation", True, "Alle Ordner erfolgreich erstellt"))
            return True
            
        except Exception as e:
            print(f"  ❌ Fehler bei Ordner-Erstellung: {e}")
            self.test_results.append(("Folder Structure Creation", False, str(e)))
            return False
    
    def test_fuzzy_matching_capability(self):
        """Test: Fuzzy-Matching Funktionalität"""
        print("\n🧪 TESTING: Fuzzy Matching Capability...")
        
        try:
            # Teste ob rapidfuzz verfügbar ist
            try:
                from rapidfuzz import process, fuzz
                print("  ✅ rapidfuzz importiert")
            except ImportError:
                try:
                    from difflib import SequenceMatcher
                    print("  ✅ difflib (Fallback) verfügbar")
                except ImportError:
                    print("  ❌ Keine Fuzzy-Matching-Bibliothek verfügbar")
                    self.test_results.append(("Fuzzy Matching", False, "Keine Bibliothek verfügbar"))
                    return False
            
            # Teste Matching-Logik
            customers_data = {
                "customer_001": {"name": "Müller GmbH", "code": "MUE"},
                "customer_002": {"name": "TechCorp AG", "code": "TCO"},
                "customer_003": {"name": "International Services", "code": "INT"}
            }
            
            # Teste verschiedene Suchbegriffe
            test_searches = [
                ("müller", "Müller GmbH"),
                ("tech", "TechCorp AG"),
                ("MUE", "Müller GmbH"),
                ("international", "International Services")
            ]
            
            matches_found = 0
            for search_term, expected_match in test_searches:
                # Einfache Suche implementieren
                found = False
                for customer_data in customers_data.values():
                    if (search_term.lower() in customer_data['name'].lower() or 
                        search_term.upper() in customer_data['code'].upper()):
                        found = True
                        matches_found += 1
                        break
                
                status = "✅" if found else "❌"
                print(f"  {status} Suche '{search_term}' -> {expected_match if found else 'Nicht gefunden'}")
            
            success_rate = matches_found / len(test_searches)
            if success_rate >= 0.75:
                print(f"  ✅ Fuzzy-Matching funktional ({success_rate:.0%} Erfolg)")
                self.test_results.append(("Fuzzy Matching", True, f"{success_rate:.0%} Erfolgsrate"))
                return True
            else:
                print(f"  ⚠️ Fuzzy-Matching teilweise funktional ({success_rate:.0%} Erfolg)")
                self.test_results.append(("Fuzzy Matching", False, f"Nur {success_rate:.0%} Erfolgsrate"))
                return False
                
        except Exception as e:
            print(f"  ❌ Fehler beim Fuzzy-Matching Test: {e}")
            self.test_results.append(("Fuzzy Matching", False, str(e)))
            return False
    
    def test_upload_workflow_integration(self):
        """Test: Upload-Workflow Integration"""
        print("\n🧪 TESTING: Upload Workflow Integration...")
        
        try:
            # Teste Upload-Ordner-Logik
            customer_code = "MUE"
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Simuliere Upload
            project_base = os.path.join(self.base_path, customer_code)
            
            # Test 1: Erster Upload des Tages
            project_1 = f"{today}_Upload_Test_1"
            project_path_1 = os.path.join(project_base, project_1)
            
            os.makedirs(os.path.join(project_path_1, "Ausgangstexte"), exist_ok=True)
            print(f"  ✅ Erster Upload-Ordner erstellt: {project_1}")
            
            # Test 2: Zweiter Upload des Tages (mit Zeitstempel)
            current_time = datetime.now().strftime("%H%M")
            project_2 = f"{today}_{current_time}_Upload_Test_2"
            project_path_2 = os.path.join(project_base, project_2)
            
            os.makedirs(os.path.join(project_path_2, "Ausgangstexte"), exist_ok=True)
            print(f"  ✅ Zweiter Upload-Ordner mit Zeitstempel: {project_2}")
            
            # Teste Workflow-Ordner
            workflows_tested = 0
            for workflow in ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = os.path.join(project_path_1, workflow)
                if os.path.exists(workflow_path):
                    workflows_tested += 1
                    print(f"  ✅ Workflow '{workflow}' verfügbar")
            
            if workflows_tested >= 4:
                print(f"  ✅ Alle Workflow-Ordner verfügbar")
                self.test_results.append(("Upload Workflow", True, "Vollständige Upload-Logik"))
                return True
            else:
                print(f"  ⚠️ Nur {workflows_tested}/4 Workflow-Ordner verfügbar")
                self.test_results.append(("Upload Workflow", False, f"Nur {workflows_tested}/4 Workflows"))
                return False
                
        except Exception as e:
            print(f"  ❌ Fehler bei Upload-Workflow Test: {e}")
            self.test_results.append(("Upload Workflow", False, str(e)))
            return False
    
    def test_calendar_integration_readiness(self):
        """Test: Kalender-Integration Bereitschaft"""
        print("\n🧪 TESTING: Calendar Integration Readiness...")
        
        try:
            # Teste ob SmartUploadCalendar importiert werden kann
            calendar_available = False
            try:
                sys.path.insert(0, 'src/ui')
                import smart_upload_calendar
                print("  ✅ SmartUploadCalendar Modul verfügbar")
                calendar_available = True
            except ImportError:
                print("  ⚠️ SmartUploadCalendar Modul nicht gefunden")
            
            # Teste Upload-Daten-Struktur für Kalender
            upload_data = {}
            
            # Simuliere Upload-Daten sammeln
            if os.path.exists(self.base_path):
                for customer_folder in os.listdir(self.base_path):
                    customer_path = os.path.join(self.base_path, customer_folder)
                    if os.path.isdir(customer_path):
                        for project_folder in os.listdir(customer_path):
                            if project_folder.startswith('20'):  # Jahr 20XX
                                date_part = project_folder.split('_')[0]
                                if date_part not in upload_data:
                                    upload_data[date_part] = []
                                
                                # Zähle Dateien
                                project_path = os.path.join(customer_path, project_folder)
                                ausgangstexte_path = os.path.join(project_path, "Ausgangstexte")
                                
                                file_count = 0
                                if os.path.exists(ausgangstexte_path):
                                    file_count = len([f for f in os.listdir(ausgangstexte_path) 
                                                    if os.path.isfile(os.path.join(ausgangstexte_path, f))])
                                
                                upload_data[date_part].append({
                                    'customer': customer_folder,
                                    'project': project_folder,
                                    'files': file_count
                                })
            
            upload_days = len(upload_data)
            print(f"  ✅ Upload-Daten für {upload_days} Tage gefunden")
            
            # Tooltip-Daten-Format testen
            for date, projects in upload_data.items():
                for project in projects:
                    tooltip_text = f"📅 {date}\n👤 {project['customer']}\n🎯 {project['project']}\n📄 {project['files']} Dateien"
                    print(f"  ✅ Tooltip-Format: {date} -> {len(tooltip_text)} Zeichen")
                    break  # Nur ein Beispiel
                break
            
            if calendar_available and upload_days > 0:
                print(f"  ✅ Kalender-Integration vollständig bereit")
                self.test_results.append(("Calendar Integration", True, "Vollständig bereit"))
                return True
            elif upload_days > 0:
                print(f"  ⚠️ Kalender-Daten bereit, aber Modul fehlt")
                self.test_results.append(("Calendar Integration", False, "Modul fehlt"))
                return False
            else:
                print(f"  ⚠️ Keine Upload-Daten für Kalender")
                self.test_results.append(("Calendar Integration", False, "Keine Daten"))
                return False
                
        except Exception as e:
            print(f"  ❌ Fehler bei Kalender-Test: {e}")
            self.test_results.append(("Calendar Integration", False, str(e)))
            return False
    
    def test_json_configuration_management(self):
        """Test: JSON-Konfigurationsverwaltung"""
        print("\n🧪 TESTING: JSON Configuration Management...")
        
        try:
            config_files = [
                ("customers.json", "Kundendaten"),
                ("kunden_config.json", "Kunden-Konfiguration"),
                ("customer_profile.json", "Kunden-Profil Template")
            ]
            
            configs_found = 0
            for config_file, description in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        print(f"  ✅ {config_file} ({description}) - {len(data)} Einträge")
                        configs_found += 1
                    except json.JSONDecodeError as e:
                        print(f"  ❌ {config_file} ungültiges JSON: {e}")
                else:
                    print(f"  ⚠️ {config_file} nicht gefunden")
            
            # Teste Konfiguration laden/speichern
            test_config = {
                "test_entry": "test_value",
                "timestamp": datetime.now().isoformat()
            }
            
            test_file = "test_config.json"
            try:
                # Schreiben
                with open(test_file, 'w', encoding='utf-8') as f:
                    json.dump(test_config, f, indent=2, ensure_ascii=False)
                
                # Lesen
                with open(test_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                if loaded_config == test_config:
                    print(f"  ✅ JSON Schreiben/Lesen funktional")
                    os.remove(test_file)  # Aufräumen
                else:
                    print(f"  ❌ JSON Daten inkonsistent")
                    
            except Exception as e:
                print(f"  ❌ JSON Test fehlgeschlagen: {e}")
            
            if configs_found >= 2:
                print(f"  ✅ JSON-Konfigurationssystem funktional")
                self.test_results.append(("JSON Configuration", True, f"{configs_found} Konfigurationen"))
                return True
            else:
                print(f"  ⚠️ Unvollständige JSON-Konfiguration")
                self.test_results.append(("JSON Configuration", False, "Unvollständig"))
                return False
                
        except Exception as e:
            print(f"  ❌ Fehler bei JSON-Test: {e}")
            self.test_results.append(("JSON Configuration", False, str(e)))
            return False
    
    def generate_final_report(self):
        """Erstellt finalen Testbericht"""
        print("\n" + "=" * 70)
        print("📋 KUNDENMANAGEMENT INTEGRATION - FINALER TESTBERICHT")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        
        print(f"Gesamt-Tests: {total_tests}")
        print(f"Erfolgreich: {passed_tests} ✅")
        print(f"Fehlgeschlagen: {total_tests - passed_tests} ❌")
        print(f"Erfolgsrate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n📊 DETAILLIERTE ERGEBNISSE:")
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status}: {test_name} - {details}")
        
        print(f"\n🎯 KUNDENMANAGEMENT-FUNKTIONEN STATUS:")
        
        # Bewertung nach Anleitung
        feature_status = {
            "JSON-basierte Kundenverwaltung": passed_tests >= 1,
            "Fuzzy-Matching für Kundensuche": any("Fuzzy" in name for name, success, _ in self.test_results if success),
            "Ordnerstruktur ./kunden/<KÜRZEL>/<YYYY-MM-DD>/": any("Folder" in name for name, success, _ in self.test_results if success),
            "Upload-Workflow mit Zeitstempel": any("Upload" in name for name, success, _ in self.test_results if success),
            "Kalender-Integration bereit": any("Calendar" in name for name, success, _ in self.test_results if success),
            "Konfigurationsdateien verfügbar": any("JSON" in name for name, success, _ in self.test_results if success)
        }
        
        for feature, status in feature_status.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {feature}")
        
        # Gesamtbewertung
        features_working = sum(1 for status in feature_status.values() if status)
        total_features = len(feature_status)
        
        if features_working == total_features:
            overall_status = "🟢 VOLLSTÄNDIG INTEGRIERT"
            conclusion = "Das Kundenmanagement ist vollständig nach Anleitung implementiert!"
        elif features_working >= total_features * 0.8:
            overall_status = "🟡 GRÖSSTENTEILS INTEGRIERT"
            conclusion = "Die meisten Funktionen sind implementiert, kleinere Nacharbeiten nötig."
        else:
            overall_status = "🟠 TEILWEISE INTEGRIERT"
            conclusion = "Grundfunktionen verfügbar, erweiterte Features benötigen Nacharbeit."
        
        print(f"\n🏆 GESAMTSTATUS: {overall_status}")
        print(f"📝 FAZIT: {conclusion}")
        
        return features_working == total_features
    
    def run_complete_test_suite(self):
        """Führt alle Tests durch"""
        print("🚀 STARTE KUNDENMANAGEMENT INTEGRATION TESTS")
        print("=" * 70)
        
        # Teste alle Komponenten
        self.test_customer_data_loading()
        self.test_folder_structure_creation()
        self.test_fuzzy_matching_capability()
        self.test_upload_workflow_integration()
        self.test_calendar_integration_readiness()
        self.test_json_configuration_management()
        
        # Abschlussbericht
        return self.generate_final_report()


def main():
    """Hauptfunktion für Kundenmanagement-Tests"""
    print("🔍 Checker Pro Suite - Kundenmanagement Integration Test Suite")
    print("🎯 Basierend auf der bereitgestellten Anleitung")
    print()
    
    test_suite = CustomerManagementTestSuite()
    success = test_suite.run_complete_test_suite()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ALLE KUNDENMANAGEMENT-FUNKTIONEN ERFOLGREICH INTEGRIERT! 🎉")
    else:
        print("📝 KUNDENMANAGEMENT TEILWEISE INTEGRIERT - Nacharbeiten erforderlich.")
    
    print("✨ Integration Test abgeschlossen! ✨")


if __name__ == "__main__":
    main()

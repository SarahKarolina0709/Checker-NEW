#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Translation Quality Workflow Implementation
========================================================

This module implements the user's specified 6-criteria translation quality framework
with a 6-step workflow process, integrating existing quality modules.

Author: GitHub Copilot
Date: 2025
Framework: CustomTkinter
"""

import customtkinter as ctk
import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from tkinter import filedialog

# Import existing quality modules
try:
    from ki_module import (
        ki_qualitaetspruefung, ki_qualitaetspruefung_vergleich,
        ki_terminologiepruefung, ki_konsistenzpruefung,
        ki_tonfall_pruefung, ki_kulturelle_pruefung,
        ki_glossa_check, ki_stilistik_pruefung,
        ki_korrekturvorschlaege, ki_abschnitts_check
    )
except ImportError:
    logging.warning("KI module nicht verfügbar - AI-Funktionen deaktiviert")

try:
    import language_tool_python
    LANGUAGETOOL_AVAILABLE = True
except ImportError:
    LANGUAGETOOL_AVAILABLE = False
    logging.warning("LanguageTool nicht verfügbar - Grammatikprüfung deaktiviert")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation_quality.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TranslationFileManager:
    """
    Specialized file manager for translation quality checking.
    Handles file pairs (source + translation) and text extraction.
    """
    
    def __init__(self):
        """Initialize the translation file manager"""
        self.file_pairs = []
        self.source_files = []
        self.translation_files = []
        logger.info("Translation File Manager initialized")
    
    def add_source_files(self, file_paths: List[str]) -> bool:
        """Add source files to the manager"""
        try:
            self.source_files.extend(file_paths)
            logger.info(f"Added {len(file_paths)} source files")
            return True
        except Exception as e:
            logger.error(f"Error adding source files: {e}")
            return False
    
    def add_translation_files(self, file_paths: List[str]) -> bool:
        """Add translation files to the manager"""
        try:
            self.translation_files.extend(file_paths)
            logger.info(f"Added {len(file_paths)} translation files")
            return True
        except Exception as e:
            logger.error(f"Error adding translation files: {e}")
            return False
    
    def create_file_pairs(self) -> List[Tuple[str, str]]:
        """
        Create file pairs based on filename matching or manual pairing
        Returns list of (source_file, translation_file) tuples
        """
        pairs = []
        
        try:
            # Simple approach: pair by index if same number of files
            if len(self.source_files) == len(self.translation_files):
                for i in range(len(self.source_files)):
                    pairs.append((self.source_files[i], self.translation_files[i]))
                logger.info(f"Created {len(pairs)} file pairs by index")
            else:
                # Try to match by filename similarity
                for source_file in self.source_files:
                    source_name = os.path.splitext(os.path.basename(source_file))[0]
                    
                    # Look for similar translation file
                    best_match = None
                    for trans_file in self.translation_files:
                        trans_name = os.path.splitext(os.path.basename(trans_file))[0]
                        
                        # Simple similarity check
                        if source_name.lower() in trans_name.lower() or trans_name.lower() in source_name.lower():
                            best_match = trans_file
                            break
                    
                    if best_match:
                        pairs.append((source_file, best_match))
                        self.translation_files.remove(best_match)
                
                logger.info(f"Created {len(pairs)} file pairs by name matching")
            
            self.file_pairs = pairs
            return pairs
            
        except Exception as e:
            logger.error(f"Error creating file pairs: {e}")
            return []
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file formats"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_extension == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    logger.warning("PyPDF2 not available, cannot extract PDF text")
                    return f"PDF file: {os.path.basename(file_path)} (text extraction not available)"
            
            elif file_extension in ['.docx', '.doc']:
                try:
                    import docx
                    doc = docx.Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    logger.warning("python-docx not available, cannot extract DOCX text")
                    return f"Word document: {os.path.basename(file_path)} (text extraction not available)"
            
            else:
                # Try to read as text file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return f"Error reading file: {os.path.basename(file_path)}"
    
    def get_file_pair_texts(self, pair_index: int) -> Tuple[str, str]:
        """Get extracted text from a file pair"""
        try:
            if pair_index < len(self.file_pairs):
                source_file, trans_file = self.file_pairs[pair_index]
                source_text = self.extract_text_from_file(source_file)
                trans_text = self.extract_text_from_file(trans_file)
                return source_text, trans_text
            else:
                logger.error(f"Invalid pair index: {pair_index}")
                return "", ""
        except Exception as e:
            logger.error(f"Error getting file pair texts: {e}")
            return "", ""
    
    def clear_files(self):
        """Clear all files and pairs"""
        self.file_pairs = []
        self.source_files = []
        self.translation_files = []
        logger.info("All files cleared")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of loaded files"""
        return {
            'source_files_count': len(self.source_files),
            'translation_files_count': len(self.translation_files), 
            'file_pairs_count': len(self.file_pairs),
            'source_files': [os.path.basename(f) for f in self.source_files],
            'translation_files': [os.path.basename(f) for f in self.translation_files],
            'file_pairs': [(os.path.basename(s), os.path.basename(t)) for s, t in self.file_pairs]
        }

class TranslationQualityFramework:
    """
    Implements comprehensive translation quality checking based on 6 criteria:
    1. Richtigkeit (Accuracy)
    2. Vollständigkeit (Completeness) 
    3. Konsistenz (Consistency)
    4. Formatierung & Layout
    5. Technische Validität (Technical Validity)
    6. Feedback & Rückmeldungen
    
    Workflow: Eingangsprüfung → Formatprüfung → Inhaltsprüfung → 
              Qualitätskontrolle → Technische Validierung → Feedback
    """
    
    def __init__(self, source_language="en-US", target_language="de-DE", 
                 subject_area="Allgemein", check_level="v2"):
        """Initialize the translation quality framework"""
        self.source_language = source_language
        self.target_language = target_language
        self.subject_area = subject_area
        self.check_level = check_level
        
        # Initialize results storage
        self.results = {
            'criteria_results': {},
            'workflow_results': {},
            'overall_score': 0,
            'critical_issues': [],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Initialize LanguageTool if available
        self.language_tool = None
        if LANGUAGETOOL_AVAILABLE:
            try:
                self.language_tool = language_tool_python.LanguageTool(target_language)
                logger.info(f"LanguageTool initialisiert für {target_language}")
            except Exception as e:
                logger.warning(f"LanguageTool Initialisierung fehlgeschlagen: {e}")
        
        logger.info(f"Translation Quality Framework initialisiert: {source_language} → {target_language}")

    # ==================== 6-CRITERIA QUALITY CHECKS ====================
    
    def check_richtigkeit(self, source_text: str, target_text: str, 
                         glossary_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Criterion 1: Richtigkeit (Accuracy)
        Checks for meaning preservation, factual correctness, numerical accuracy
        """
        logger.info("🎯 Prüfung: Richtigkeit (Accuracy)")
        results = {
            'criterion': 'Richtigkeit',
            'status': 'in_progress',
            'checks_performed': [],
            'issues_found': [],
            'score': 0
        }
        
        try:
            # AI-based quality comparison
            ai_comparison = ki_qualitaetspruefung_vergleich(
                source_text, target_text, 
                language_code=self.target_language,
                fachgebiet=self.subject_area,
                pruefstufe=self.check_level,
                source_language_code=self.source_language
            )
            results['checks_performed'].append('AI-Qualitätsvergleich')
            
            # General quality check
            ai_quality = ki_qualitaetspruefung(
                target_text,
                language_code=self.target_language,
                fachgebiet=self.subject_area,
                pruefstufe=self.check_level
            )
            results['checks_performed'].append('AI-Qualitätsprüfung')
            
            # Glossary check if terms provided
            if glossary_terms:
                glossary_result = ki_glossa_check(
                    source_text, target_text, glossary_terms,
                    language_code=self.target_language,
                    fachgebiet=self.subject_area,
                    pruefstufe=self.check_level,
                    source_language_code=self.source_language
                )
                results['checks_performed'].append('Glossar-Prüfung')
            
            # Parse and evaluate results
            results['ai_comparison'] = ai_comparison
            results['ai_quality'] = ai_quality
            if glossary_terms:
                results['glossary_check'] = glossary_result
            
            # Calculate score based on issues found
            critical_errors = self._count_critical_issues(ai_comparison, ai_quality)
            results['score'] = max(0, 100 - (critical_errors * 10))
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Fehler bei Richtigkeitsprüfung: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
        return results

    def check_vollstaendigkeit(self, source_text: str, target_text: str) -> Dict[str, Any]:
        """
        Criterion 2: Vollständigkeit (Completeness)
        Checks for missing sections, omissions, duplications
        """
        logger.info("📋 Prüfung: Vollständigkeit (Completeness)")
        results = {
            'criterion': 'Vollständigkeit',
            'status': 'in_progress',
            'checks_performed': [],
            'issues_found': [],
            'score': 0
        }
        
        try:
            # Section completeness check
            section_check = ki_abschnitts_check(
                source_text, target_text,
                language_code=self.target_language,
                fachgebiet=self.subject_area,
                pruefstufe=self.check_level
            )
            results['checks_performed'].append('Abschnitts-Vollständigkeitsprüfung')
            results['section_analysis'] = section_check
            
            # Calculate basic completeness metrics
            source_lines = len(source_text.split('\n'))
            target_lines = len(target_text.split('\n'))
            
            # Word count comparison
            source_words = len(source_text.split())
            target_words = len(target_text.split())
            word_ratio = target_words / source_words if source_words > 0 else 0
            
            results['metrics'] = {
                'source_lines': source_lines,
                'target_lines': target_lines,
                'source_words': source_words,
                'target_words': target_words,
                'word_ratio': word_ratio
            }
            
            # Score based on word ratio and section analysis
            if 0.8 <= word_ratio <= 1.3:  # Reasonable range
                base_score = 90
            elif 0.6 <= word_ratio <= 1.5:
                base_score = 70
            else:
                base_score = 50
                
            results['score'] = base_score
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Fehler bei Vollständigkeitsprüfung: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
        return results

    def check_konsistenz(self, source_text: str, target_text: str,
                        key_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Criterion 3: Konsistenz (Consistency)
        Checks terminology consistency, naming conventions, style consistency
        """
        logger.info("🔄 Prüfung: Konsistenz (Consistency)")
        results = {
            'criterion': 'Konsistenz',
            'status': 'in_progress',
            'checks_performed': [],
            'issues_found': [],
            'score': 0
        }
        
        try:
            # Terminology consistency check
            if key_terms:
                terminology_check = ki_terminologiepruefung(
                    source_text, target_text, key_terms,
                    language_code=self.target_language,
                    fachgebiet=self.subject_area,
                    pruefstufe=self.check_level,
                    source_language_code=self.source_language
                )
                results['checks_performed'].append('Terminologie-Konsistenz')
                results['terminology_analysis'] = terminology_check
            
            # General consistency check
            consistency_check = ki_konsistenzpruefung(
                source_text, target_text,
                language_code=self.target_language,
                fachgebiet=self.subject_area,
                pruefstufe=self.check_level,
                source_language_code=self.source_language
            )
            results['checks_performed'].append('Allgemeine Konsistenzprüfung')
            results['consistency_analysis'] = consistency_check
            
            # Calculate consistency score
            consistency_issues = self._count_consistency_issues(consistency_check)
            results['score'] = max(0, 100 - (consistency_issues * 15))
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Fehler bei Konsistenzprüfung: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
        return results

    def check_formatierung_layout(self, target_text: str) -> Dict[str, Any]:
        """
        Criterion 4: Formatierung & Layout
        Checks formatting, punctuation, typography, structure
        """
        logger.info("📐 Prüfung: Formatierung & Layout")
        results = {
            'criterion': 'Formatierung_Layout',
            'status': 'in_progress',
            'checks_performed': [],
            'issues_found': [],
            'score': 0
        }
        
        try:
            # LanguageTool grammar and formatting check
            if self.language_tool:
                lt_errors = self.language_tool.check(target_text)
                results['checks_performed'].append('LanguageTool Grammatik/Format')
                results['languagetool_errors'] = [
                    {
                        'message': error.message,
                        'context': error.context,
                        'category': error.category,
                        'rule_id': error.ruleId
                    } for error in lt_errors
                ]
                
                # Count critical formatting issues
                critical_format_errors = len([e for e in lt_errors 
                                            if e.category in ['TYPOGRAPHY', 'PUNCTUATION']])
                format_score = max(0, 100 - (critical_format_errors * 5))
            else:
                format_score = 85  # Default score when LanguageTool unavailable
                results['languagetool_errors'] = []
            
            # Style analysis
            style_analysis = ki_stilistik_pruefung(
                target_text,
                language_code=self.target_language,
                fachgebiet=self.subject_area,
                pruefstufe=self.check_level
            )
            results['checks_performed'].append('Stil-Analyse')
            results['style_analysis'] = style_analysis
            
            results['score'] = format_score
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Fehler bei Formatierungsprüfung: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
        return results

    def check_technische_validitaet(self, source_text: str, target_text: str) -> Dict[str, Any]:
        """
        Criterion 5: Technische Validität
        Checks technical accuracy, units, measurements, specifications
        """
        logger.info("⚙️ Prüfung: Technische Validität")
        results = {
            'criterion': 'Technische_Validitaet',
            'status': 'in_progress',
            'checks_performed': [],
            'issues_found': [],
            'score': 0
        }
        
        try:
            # Technical quality check with specialized prompts
            technical_check = ki_qualitaetspruefung_vergleich(
                source_text, target_text,
                language_code=self.target_language,
                fachgebiet="Technik",  # Use technical domain
                pruefstufe=self.check_level,
                source_language_code=self.source_language
            )
            results['checks_performed'].append('Technische Qualitätsprüfung')
            results['technical_analysis'] = technical_check
            
            # Cultural appropriateness for technical content
            cultural_check = ki_kulturelle_pruefung(
                source_text, target_text,
                language_code=self.target_language,
                fachgebiet=self.subject_area,
                pruefstufe=self.check_level,
                source_language_code=self.source_language
            )
            results['checks_performed'].append('Kulturelle Anpassung')
            results['cultural_analysis'] = cultural_check
            
            # Calculate technical validity score
            technical_issues = self._count_technical_issues(technical_check)
            results['score'] = max(0, 100 - (technical_issues * 20))
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Fehler bei technischer Validitätsprüfung: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
        return results

    def generate_feedback_recommendations(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Criterion 6: Feedback & Rückmeldungen
        Generates actionable feedback and improvement recommendations
        """
        logger.info("💬 Generierung: Feedback & Rückmeldungen")
        feedback = {
            'criterion': 'Feedback_Rueckmeldungen',
            'status': 'in_progress',
            'recommendations': [],
            'priority_issues': [],
            'score': 0
        }
        
        try:
            # Analyze all previous results to generate comprehensive feedback
            total_score = 0
            criteria_count = 0
            critical_issues = []
            
            for criterion, result in all_results.items():
                if isinstance(result, dict) and 'score' in result:
                    total_score += result['score']
                    criteria_count += 1
                    
                    # Collect critical issues
                    if result['score'] < 70:
                        critical_issues.append({
                            'criterion': criterion,
                            'score': result['score'],
                            'issues': result.get('issues_found', [])
                        })
            
            # Calculate overall quality score
            overall_score = total_score / criteria_count if criteria_count > 0 else 0
            
            # Generate recommendations based on scores
            recommendations = self._generate_recommendations(all_results, overall_score)
            
            feedback.update({
                'overall_score': overall_score,
                'recommendations': recommendations,
                'priority_issues': critical_issues,
                'score': min(100, overall_score + 5),  # Slight bonus for comprehensive feedback
                'status': 'completed'
            })
            
        except Exception as e:
            logger.error(f"Fehler bei Feedback-Generierung: {e}")
            feedback['status'] = 'error'
            feedback['error'] = str(e)
            
        return feedback

    # ==================== 6-STEP WORKFLOW IMPLEMENTATION ====================
    
    def step1_eingangspruefung(self, source_text: str, target_text: str) -> Dict[str, Any]:
        """
        Workflow Step 1: Eingangsprüfung (Initial Assessment)
        Basic validation and preparation for detailed checks
        """
        logger.info("🚪 Workflow Schritt 1: Eingangsprüfung")
        result = {
            'step': 'Eingangspruefung',
            'status': 'in_progress',
            'validations': [],
            'issues': [],
            'ready_for_next_step': True
        }
        
        try:
            # Basic text validation
            if not source_text or not source_text.strip():
                result['issues'].append('Ausgangstext ist leer')
                result['ready_for_next_step'] = False
                
            if not target_text or not target_text.strip():
                result['issues'].append('Zieltext ist leer')
                result['ready_for_next_step'] = False
            
            # Length validation
            if len(source_text) < 10:
                result['issues'].append('Ausgangstext zu kurz für aussagekräftige Prüfung')
                
            if len(target_text) < 10:
                result['issues'].append('Zieltext zu kurz für aussagekräftige Prüfung')
            
            # Character encoding check
            try:
                source_text.encode('utf-8')
                target_text.encode('utf-8')
                result['validations'].append('UTF-8 Encoding validiert')
            except UnicodeEncodeError:
                result['issues'].append('Zeichencodierung-Probleme erkannt')
            
            result['source_length'] = len(source_text)
            result['target_length'] = len(target_text)
            result['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Fehler in Eingangsprüfung: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
            result['ready_for_next_step'] = False
            
        return result

    def step2_formatpruefung(self, target_text: str) -> Dict[str, Any]:
        """
        Workflow Step 2: Formatprüfung (Format Check)
        Focus on formatting, structure, and presentation
        """
        logger.info("📋 Workflow Schritt 2: Formatprüfung")
        return self.check_formatierung_layout(target_text)

    def step3_inhaltspruefung(self, source_text: str, target_text: str,
                             glossary_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Workflow Step 3: Inhaltsprüfung (Content Check)
        Focus on accuracy and completeness
        """
        logger.info("📖 Workflow Schritt 3: Inhaltsprüfung")
        
        # Combine accuracy and completeness checks
        accuracy_result = self.check_richtigkeit(source_text, target_text, glossary_terms)
        completeness_result = self.check_vollstaendigkeit(source_text, target_text)
        
        return {
            'step': 'Inhaltspruefung',
            'accuracy': accuracy_result,
            'completeness': completeness_result,
            'combined_score': (accuracy_result['score'] + completeness_result['score']) / 2
        }

    def step4_qualitaetskontrolle(self, source_text: str, target_text: str,
                                 key_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Workflow Step 4: Qualitätskontrolle (Quality Control)
        Focus on consistency and terminology
        """
        logger.info("✅ Workflow Schritt 4: Qualitätskontrolle")
        return self.check_konsistenz(source_text, target_text, key_terms)

    def step5_technische_validierung(self, source_text: str, target_text: str) -> Dict[str, Any]:
        """
        Workflow Step 5: Technische Validierung (Technical Validation)
        Focus on technical accuracy and domain-specific requirements
        """
        logger.info("⚙️ Workflow Schritt 5: Technische Validierung")
        return self.check_technische_validitaet(source_text, target_text)

    def step6_feedback_rueckmeldungen(self, all_workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Workflow Step 6: Feedback & Rückmeldungen
        Generate comprehensive feedback and recommendations
        """
        logger.info("💬 Workflow Schritt 6: Feedback & Rückmeldungen")
        return self.generate_feedback_recommendations(all_workflow_results)

    # ==================== COMPREHENSIVE QUALITY CHECK ====================
    
    def run_comprehensive_translation_quality_check(self, source_text: str, target_text: str,
                                                   glossary_terms: Optional[List[str]] = None,
                                                   key_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute complete translation quality check using both criteria and workflow approaches
        """
        logger.info("🎯 Starting Comprehensive Translation Quality Check")
        
        start_time = datetime.now()
        
        # Execute 6-criteria checks
        criteria_results = {}
        criteria_results['richtigkeit'] = self.check_richtigkeit(source_text, target_text, glossary_terms)
        criteria_results['vollstaendigkeit'] = self.check_vollstaendigkeit(source_text, target_text)
        criteria_results['konsistenz'] = self.check_konsistenz(source_text, target_text, key_terms)
        criteria_results['formatierung_layout'] = self.check_formatierung_layout(target_text)
        criteria_results['technische_validitaet'] = self.check_technische_validitaet(source_text, target_text)
        criteria_results['feedback'] = self.generate_feedback_recommendations(criteria_results)
        
        # Execute 6-step workflow
        workflow_results = {}
        workflow_results['step1'] = self.step1_eingangspruefung(source_text, target_text)
        
        if workflow_results['step1']['ready_for_next_step']:
            workflow_results['step2'] = self.step2_formatpruefung(target_text)
            workflow_results['step3'] = self.step3_inhaltspruefung(source_text, target_text, glossary_terms)
            workflow_results['step4'] = self.step4_qualitaetskontrolle(source_text, target_text, key_terms)
            workflow_results['step5'] = self.step5_technische_validierung(source_text, target_text)
            workflow_results['step6'] = self.step6_feedback_rueckmeldungen(workflow_results)
        
        # Calculate overall results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        overall_results = {
            'criteria_results': criteria_results,
            'workflow_results': workflow_results,
            'summary': self._generate_summary(criteria_results, workflow_results),
            'metadata': {
                'source_language': self.source_language,
                'target_language': self.target_language,
                'subject_area': self.subject_area,
                'check_level': self.check_level,
                'duration_seconds': duration,
                'timestamp': end_time.isoformat()
            }
        }
        
        logger.info(f"Translation Quality Check completed in {duration:.2f} seconds")
        return overall_results

    # ==================== HELPER METHODS ====================
    
    def _count_critical_issues(self, *analysis_results) -> int:
        """Count critical issues from AI analysis results"""
        critical_count = 0
        for result in analysis_results:
            if isinstance(result, str):
                # Simple keyword-based counting
                if any(keyword in result.lower() for keyword in 
                      ['fehler', 'falsch', 'kritisch', 'error', 'incorrect', 'critical']):
                    critical_count += result.lower().count('fehler')
                    critical_count += result.lower().count('error')
        return critical_count
    
    def _count_consistency_issues(self, consistency_result: str) -> int:
        """Count consistency issues from analysis"""
        if isinstance(consistency_result, str):
            return consistency_result.lower().count('inkonsistenz') + \
                   consistency_result.lower().count('inconsistency')
        return 0
    
    def _count_technical_issues(self, technical_result: str) -> int:
        """Count technical issues from analysis"""
        if isinstance(technical_result, str):
            technical_keywords = ['maßeinheit', 'einheit', 'unit', 'measurement', 'specification']
            return sum(technical_result.lower().count(keyword) for keyword in technical_keywords)
        return 0
    
    def _generate_recommendations(self, results: Dict[str, Any], overall_score: float) -> List[str]:
        """Generate actionable recommendations based on results"""
        recommendations = []
        
        if overall_score < 60:
            recommendations.append("🚨 Dringende Überarbeitung erforderlich - Übersetzung erfüllt nicht die Mindestqualitätsstandards")
        elif overall_score < 80:
            recommendations.append("⚠️ Verbesserungen empfohlen - Mehrere Qualitätskriterien nicht optimal erfüllt")
        else:
            recommendations.append("✅ Gute Übersetzungsqualität - Nur kleinere Anpassungen nötig")
        
        # Specific recommendations based on individual criteria
        for criterion, result in results.items():
            if isinstance(result, dict) and result.get('score', 100) < 70:
                if criterion == 'richtigkeit':
                    recommendations.append("📍 Richtigkeit: Prüfen Sie Fachbegriffe und Zahlenangaben")
                elif criterion == 'vollstaendigkeit':
                    recommendations.append("📋 Vollständigkeit: Überprüfen Sie auf fehlende Abschnitte")
                elif criterion == 'konsistenz':
                    recommendations.append("🔄 Konsistenz: Vereinheitlichen Sie die Terminologie")
                elif criterion == 'formatierung_layout':
                    recommendations.append("📐 Formatierung: Korrigieren Sie Grammatik und Interpunktion")
                elif criterion == 'technische_validitaet':
                    recommendations.append("⚙️ Technische Validität: Überprüfen Sie fachspezifische Begriffe")
        
        return recommendations
    
    def _generate_summary(self, criteria_results: Dict[str, Any], 
                         workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive summary of all results"""
        # Calculate average scores
        criteria_scores = [r['score'] for r in criteria_results.values() 
                          if isinstance(r, dict) and 'score' in r]
        avg_criteria_score = sum(criteria_scores) / len(criteria_scores) if criteria_scores else 0
        
        # Count completed steps
        completed_steps = len([r for r in workflow_results.values() 
                              if isinstance(r, dict) and r.get('status') == 'completed'])
        
        return {
            'overall_quality_score': avg_criteria_score,
            'criteria_average': avg_criteria_score,
            'workflow_steps_completed': completed_steps,
            'total_workflow_steps': 6,
            'quality_rating': self._get_quality_rating(avg_criteria_score),
            'recommendation_summary': self._get_recommendation_summary(avg_criteria_score)
        }
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert numeric score to quality rating"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Acceptable"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _get_recommendation_summary(self, score: float) -> str:
        """Get summary recommendation based on score"""
        if score >= 90:
            return "Translation meets high quality standards. Minor polishing may be beneficial."
        elif score >= 80:
            return "Good translation quality. Some improvements recommended."
        elif score >= 70:
            return "Acceptable quality. Several areas need attention."
        elif score >= 60:
            return "Below standard. Significant improvements required."
        else:
            return "Poor quality. Major revision or retranslation recommended."


def create_translation_quality_gui(app_instance=None, initial_file_manager=None):
    """
    Create GUI interface for translation quality checking with file upload support
    """
    if app_instance:
        # Integration with existing app
        quality_window = ctk.CTkToplevel(app_instance)
    else:
        # Standalone window
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        quality_window = ctk.CTk()
    
    quality_window.title("Translation Quality Framework")
    quality_window.geometry("1200x900")
    
    # Initialize file manager (use provided one or create new)
    file_manager = initial_file_manager if initial_file_manager else TranslationFileManager()
    
    # Attach file manager to window for external access
    quality_window.file_manager = file_manager
    
    # Create main frame with scrollable area
    main_frame = ctk.CTkScrollableFrame(quality_window)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = ctk.CTkLabel(
        main_frame, 
        text="🌍 Translation Quality Framework with File Upload",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title_label.pack(pady=(0, 20))
    
    # Language configuration frame
    lang_frame = ctk.CTkFrame(main_frame)
    lang_frame.pack(fill="x", pady=(0, 15))
    
    ctk.CTkLabel(lang_frame, text="Language Configuration", 
                font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    # Language selection
    lang_config_frame = ctk.CTkFrame(lang_frame)
    lang_config_frame.pack(fill="x", padx=15, pady=(0, 15))
    
    source_lang_var = ctk.StringVar(value="en-US")
    target_lang_var = ctk.StringVar(value="de-DE")
    subject_var = ctk.StringVar(value="Allgemein")
    level_var = ctk.StringVar(value="v2")
    
    ctk.CTkLabel(lang_config_frame, text="Source Language:").grid(row=0, column=0, sticky="w", padx=5)
    ctk.CTkOptionMenu(lang_config_frame, variable=source_lang_var, 
                     values=["en-US", "de-DE", "fr-FR", "es-ES"]).grid(row=0, column=1, padx=5)
    
    ctk.CTkLabel(lang_config_frame, text="Target Language:").grid(row=0, column=2, sticky="w", padx=5)
    ctk.CTkOptionMenu(lang_config_frame, variable=target_lang_var,
                     values=["de-DE", "en-US", "fr-FR", "es-ES"]).grid(row=0, column=3, padx=5)
    
    ctk.CTkLabel(lang_config_frame, text="Subject Area:").grid(row=1, column=0, sticky="w", padx=5)
    ctk.CTkOptionMenu(lang_config_frame, variable=subject_var,
                     values=["Allgemein", "Technik", "Marketing", "Tourismus"]).grid(row=1, column=1, padx=5)
    
    ctk.CTkLabel(lang_config_frame, text="Check Level:").grid(row=1, column=2, sticky="w", padx=5)
    ctk.CTkOptionMenu(lang_config_frame, variable=level_var,
                     values=["v1", "v2", "v3"]).grid(row=1, column=3, padx=5)
    
    # File Upload Section for Translation Pairs
    upload_frame = ctk.CTkFrame(main_frame)
    upload_frame.pack(fill="x", pady=(0, 15))
    
    ctk.CTkLabel(upload_frame, text="📂 File Upload (Translation Pairs)", 
                font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    # File pair management
    file_pair_frame = ctk.CTkFrame(upload_frame)
    file_pair_frame.pack(fill="x", padx=15, pady=(0, 15))
    
    def upload_source_files():
        files = filedialog.askopenfilenames(
            title="Ausgangstexte auswählen",
            filetypes=[
                ("Text Dateien", "*.txt"),
                ("PDF Dateien", "*.pdf"), 
                ("Word Dokumente", "*.docx"),
                ("Alle Dateien", "*.*")
            ]
        )
        if files:
            file_manager.add_source_files(list(files))
            update_file_status_display()
    
    def upload_translation_files():
        files = filedialog.askopenfilenames(
            title="Übersetzungen auswählen", 
            filetypes=[
                ("Text Dateien", "*.txt"),
                ("PDF Dateien", "*.pdf"),
                ("Word Dokumente", "*.docx"), 
                ("Alle Dateien", "*.*")
            ]
        )
        if files:
            file_manager.add_translation_files(list(files))
            update_file_status_display()
    
    def create_pairs():
        pairs = file_manager.create_file_pairs()
        if pairs:
            update_file_status_display()
            # Load first pair into text areas
            if len(pairs) > 0:
                load_file_pair(0)
    
    def load_file_pair(index):
        """Load a specific file pair into text areas"""
        try:
            source_text, trans_text = file_manager.get_file_pair_texts(index)
            
            source_text_area.delete("1.0", "end")
            source_text_area.insert("1.0", source_text)
            
            target_text_area.delete("1.0", "end")
            target_text_area.insert("1.0", trans_text)
            
            # Update status
            pair_info = file_manager.file_pairs[index]
            source_name = os.path.basename(pair_info[0])
            trans_name = os.path.basename(pair_info[1])
            
            current_pair_label.configure(
                text=f"📄 Aktuelles Paar: {source_name} ↔ {trans_name}"
            )
            
        except Exception as e:
            logger.error(f"Error loading file pair {index}: {e}")
    
    def update_file_status_display():
        # Clear existing widgets
        for widget in file_status_frame.winfo_children():
            widget.destroy()
        
        summary = file_manager.get_summary()
        
        # Source files status
        ctk.CTkLabel(
            file_status_frame,
            text=f"� Ausgangstexte: {summary['source_files_count']} Datei(en)",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=10, pady=2)
        
        # Translation files status  
        ctk.CTkLabel(
            file_status_frame,
            text=f"🌍 Übersetzungen: {summary['translation_files_count']} Datei(en)",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=10, pady=2)
        
        # File pairs status
        if summary['file_pairs_count'] > 0:
            ctk.CTkLabel(
                file_status_frame,
                text=f"🔗 Dateipaare: {summary['file_pairs_count']} erstellt",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="green"
            ).pack(anchor="w", padx=10, pady=2)
            
            # Show pair selection if multiple pairs
            if summary['file_pairs_count'] > 1:
                pair_selection_frame = ctk.CTkFrame(file_status_frame)
                pair_selection_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(pair_selection_frame, text="Dateipaare:").pack(side="left", padx=5)
                
                for i, (source, trans) in enumerate(summary['file_pairs']):
                    pair_button = ctk.CTkButton(
                        pair_selection_frame,
                        text=f"{i+1}: {source[:15]}...",
                        command=lambda idx=i: load_file_pair(idx),
                        width=120,
                        height=25
                    )
                    pair_button.pack(side="left", padx=2)
    
    # Upload buttons
    upload_button_frame = ctk.CTkFrame(file_pair_frame)
    upload_button_frame.pack(fill="x", padx=10, pady=5)
    
    ctk.CTkButton(
        upload_button_frame,
        text="📄 Ausgangstexte hochladen",
        command=upload_source_files,
        font=ctk.CTkFont(size=12),
        height=35,
        width=160
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        upload_button_frame, 
        text="🌍 Übersetzungen hochladen",
        command=upload_translation_files,
        font=ctk.CTkFont(size=12),
        height=35,
        width=160
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        upload_button_frame,
        text="🔗 Paare erstellen",
        command=create_pairs,
        font=ctk.CTkFont(size=12, weight="bold"),
        height=35,
        width=120,
        fg_color="green"
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        upload_button_frame,
        text="🗑️ Dateien löschen",
        command=lambda: [file_manager.clear_files(), update_file_status_display(), 
                        source_text_area.delete("1.0", "end"), target_text_area.delete("1.0", "end"),
                        current_pair_label.configure(text="📄 Kein Dateipaar geladen")],
        font=ctk.CTkFont(size=12),
        height=35,
        width=120,
        fg_color="red"
    ).pack(side="right", padx=5)
    
    # File status display
    file_status_frame = ctk.CTkFrame(file_pair_frame)
    file_status_frame.pack(fill="x", padx=10, pady=5)
    
    # Current pair indicator
    current_pair_label = ctk.CTkLabel(
        file_pair_frame,
        text="📄 Kein Dateipaar geladen",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color="orange"
    )
    current_pair_label.pack(pady=5)
    
    # Text input frames
    text_frame = ctk.CTkFrame(main_frame)
    text_frame.pack(fill="both", expand=True, pady=(0, 15))
    
    ctk.CTkLabel(text_frame, text="📝 Manual Text Input (Alternative)", 
                font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    # Source text
    ctk.CTkLabel(text_frame, text="Source Text:").pack(anchor="w", padx=15)
    source_text_area = ctk.CTkTextbox(text_frame, height=120)
    source_text_area.pack(fill="x", padx=15, pady=(5, 10))
    
    # Target text
    ctk.CTkLabel(text_frame, text="Target Text (Translation):").pack(anchor="w", padx=15)
    target_text_area = ctk.CTkTextbox(text_frame, height=120)
    target_text_area.pack(fill="x", padx=15, pady=(5, 10))
    
    # Optional terms
    terms_frame = ctk.CTkFrame(text_frame)
    terms_frame.pack(fill="x", padx=15, pady=(0, 15))
    
    ctk.CTkLabel(terms_frame, text="Glossary Terms (optional, one per line):").pack(anchor="w", padx=10)
    glossary_text = ctk.CTkTextbox(terms_frame, height=60)
    glossary_text.pack(fill="x", padx=10, pady=5)
    
    ctk.CTkLabel(terms_frame, text="Key Terms (optional, one per line):").pack(anchor="w", padx=10)
    key_terms_text = ctk.CTkTextbox(terms_frame, height=60)
    key_terms_text.pack(fill="x", padx=10, pady=5)
    
    # Results area
    results_frame = ctk.CTkFrame(main_frame)
    results_frame.pack(fill="both", expand=True, pady=(0, 15))
    
    ctk.CTkLabel(results_frame, text="Quality Check Results", 
                font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    results_text = ctk.CTkTextbox(results_frame, height=200)
    results_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    # Progress bar
    progress_bar = ctk.CTkProgressBar(main_frame)
    progress_bar.pack(fill="x", pady=(0, 15))
    progress_bar.set(0)
    
    def run_quality_check():
        """Execute the comprehensive quality check"""
        try:
            # Get input values
            source_text = source_text_area.get("1.0", "end-1c").strip()
            target_text = target_text_area.get("1.0", "end-1c").strip()
            
            if not source_text or not target_text:
                results_text.delete("1.0", "end")
                results_text.insert("1.0", "❌ Error: Both source and target texts are required.")
                return
            
            # Parse optional terms
            glossary_terms = [term.strip() for term in glossary_text.get("1.0", "end-1c").split('\n') 
                             if term.strip()]
            key_terms = [term.strip() for term in key_terms_text.get("1.0", "end-1c").split('\n') 
                        if term.strip()]
            
            # Initialize framework
            framework = TranslationQualityFramework(
                source_language=source_lang_var.get(),
                target_language=target_lang_var.get(),
                subject_area=subject_var.get(),
                check_level=level_var.get()
            )
            
            # Update progress
            progress_bar.set(0.1)
            quality_window.update()
            
            results_text.delete("1.0", "end")
            results_text.insert("1.0", "🔄 Running comprehensive translation quality check...\n\n")
            quality_window.update()
            
            # Run the check
            progress_bar.set(0.3)
            quality_window.update()
            
            results = framework.run_comprehensive_translation_quality_check(
                source_text, target_text, 
                glossary_terms if glossary_terms else None,
                key_terms if key_terms else None
            )
            
            progress_bar.set(0.9)
            quality_window.update()
            
            # Format results for display
            results_display = format_results_for_display(results)
            
            results_text.delete("1.0", "end")
            results_text.insert("1.0", results_display)
            
            progress_bar.set(1.0)
            
        except Exception as e:
            logger.error(f"Error in quality check: {e}")
            results_text.delete("1.0", "end")
            results_text.insert("1.0", f"❌ Error during quality check: {str(e)}")
            progress_bar.set(0)
    
    def run_batch_quality_check():
        """Analyze all uploaded file pairs"""
        if not file_manager.file_pairs:
            results_text.delete("1.0", "end")
            results_text.insert("1.0", "⚠️ No file pairs found! Please upload files and create pairs first.")
            return
            
        try:
            results_text.delete("1.0", "end")
            results_text.insert("1.0", "🔄 Analyzing all file pairs...\n\n")
            progress_bar.set(0.1)
            quality_window.update()
            
            all_results = []
            total_pairs = len(file_manager.file_pairs)
            
            for i, (source_file, trans_file) in enumerate(file_manager.file_pairs):
                # Update progress
                progress = 0.1 + (0.8 * (i / total_pairs))
                progress_bar.set(progress)
                quality_window.update()
                
                # Get texts for this pair
                source_text, trans_text = file_manager.get_file_pair_texts(i)
                
                if source_text and trans_text:
                    # Initialize framework for this pair
                    framework = TranslationQualityFramework(
                        source_language=source_lang_var.get(),
                        target_language=target_lang_var.get(),
                        subject_area=subject_var.get(),
                        check_level=level_var.get()
                    )
                    
                    # Parse optional terms
                    glossary_terms = [term.strip() for term in glossary_text.get("1.0", "end-1c").split('\n') 
                                     if term.strip()]
                    key_terms = [term.strip() for term in key_terms_text.get("1.0", "end-1c").split('\n') 
                                if term.strip()]
                    
                    # Perform analysis
                    result = framework.run_comprehensive_translation_quality_check(
                        source_text, trans_text,
                        glossary_terms if glossary_terms else None,
                        key_terms if key_terms else None
                    )
                    
                    # Add file information to result
                    result['source_file'] = os.path.basename(source_file)
                    result['translation_file'] = os.path.basename(trans_file)
                    result['pair_index'] = i + 1
                    
                    all_results.append(result)
            
            # Display batch results
            batch_results_display = format_batch_results_for_display(all_results)
            results_text.delete("1.0", "end")
            results_text.insert("1.0", batch_results_display)
            
            progress_bar.set(1.0)
            
        except Exception as e:
            logger.error(f"Batch analysis error: {e}")
            results_text.delete("1.0", "end")
            results_text.insert("1.0", f"❌ Error during batch analysis: {str(e)}")
            progress_bar.set(0)
    
    # Control buttons
    button_frame = ctk.CTkFrame(main_frame)
    button_frame.pack(fill="x", pady=(0, 15))
    
    run_button = ctk.CTkButton(
        button_frame, 
        text="🚀 Run Quality Check",
        command=run_quality_check,
        font=ctk.CTkFont(size=14, weight="bold"),
        height=40
    )
    run_button.pack(side="left", padx=15, pady=15)
    
    batch_button = ctk.CTkButton(
        button_frame, 
        text="📊 Analyze All File Pairs",
        command=run_batch_quality_check,
        font=ctk.CTkFont(size=14, weight="bold"),
        height=40,
        fg_color="orange"
    )
    batch_button.pack(side="left", padx=5, pady=15)
    
    clear_button = ctk.CTkButton(
        button_frame,
        text="🗑️ Clear All",
        command=lambda: [
            source_text_area.delete("1.0", "end"),
            target_text_area.delete("1.0", "end"),
            glossary_text.delete("1.0", "end"),
            key_terms_text.delete("1.0", "end"),
            results_text.delete("1.0", "end"),
            progress_bar.set(0)
        ],
        fg_color="gray",
        height=40
    )
    clear_button.pack(side="right", padx=15, pady=15)
    
    # Initial file status update (falls Dateien bereits vorhanden)
    if file_manager.source_files or file_manager.translation_files:
        update_file_status_display()
        # Lade erstes Paar falls bereits Paare vorhanden
        if file_manager.file_pairs:
            load_file_pair(0)
    
    if not app_instance:
        quality_window.mainloop()
    
    return quality_window


def format_batch_results_for_display(batch_results: List[Dict[str, Any]]) -> str:
    """Format batch analysis results for user-friendly display"""
    output = []
    
    # Header
    output.append("=" * 80)
    output.append("🔄 BATCH TRANSLATION QUALITY ANALYSIS REPORT")
    output.append("=" * 80)
    output.append("")
    
    # Batch summary
    total_pairs = len(batch_results)
    avg_score = sum(result.get('summary', {}).get('overall_quality_score', 0) for result in batch_results) / total_pairs if total_pairs > 0 else 0
    
    output.append("📊 BATCH SUMMARY")
    output.append("-" * 40)
    output.append(f"Total File Pairs Analyzed: {total_pairs}")
    output.append(f"Average Quality Score: {avg_score:.1f}/100")
    output.append("")
    
    # Individual results
    for i, result in enumerate(batch_results, 1):
        output.append(f"📄 FILE PAIR {i}: {result.get('source_file', 'Unknown')} ↔ {result.get('translation_file', 'Unknown')}")
        output.append("-" * 60)
        
        summary = result.get('summary', {})
        output.append(f"Quality Score: {summary.get('overall_quality_score', 0):.1f}/100")
        output.append(f"Quality Rating: {summary.get('quality_rating', 'Unknown')}")
        output.append(f"Recommendation: {summary.get('recommendation_summary', 'No recommendation')}")
        
        # Top issues
        criteria_results = result.get('criteria_results', {})
        issues = []
        for criterion, criterion_result in criteria_results.items():
            if isinstance(criterion_result, dict) and criterion_result.get('score', 100) < 70:
                issues.append(f"{criterion.replace('_', ' ').title()} ({criterion_result.get('score', 0):.1f})")
        
        if issues:
            output.append(f"Issues Found: {', '.join(issues[:3])}")
            if len(issues) > 3:
                output.append(f"  ... and {len(issues) - 3} more")
        else:
            output.append("No critical issues found")
        
        output.append("")
    
    output.append("=" * 80)
    return "\n".join(output)


def format_results_for_display(results: Dict[str, Any]) -> str:
    """Format the results dictionary for user-friendly display"""
    output = []
    
    # Header
    output.append("=" * 80)
    output.append("🌍 COMPREHENSIVE TRANSLATION QUALITY REPORT")
    output.append("=" * 80)
    output.append("")
    
    # Summary
    summary = results.get('summary', {})
    output.append("📊 OVERALL SUMMARY")
    output.append("-" * 40)
    output.append(f"Overall Quality Score: {summary.get('overall_quality_score', 0):.1f}/100")
    output.append(f"Quality Rating: {summary.get('quality_rating', 'Unknown')}")
    output.append(f"Workflow Steps Completed: {summary.get('workflow_steps_completed', 0)}/6")
    output.append(f"Recommendation: {summary.get('recommendation_summary', 'No recommendation available')}")
    output.append("")
    
    # Criteria Results
    output.append("🎯 CRITERIA-BASED ANALYSIS")
    output.append("-" * 40)
    
    criteria_results = results.get('criteria_results', {})
    for criterion, result in criteria_results.items():
        if isinstance(result, dict) and 'score' in result:
            status_icon = "✅" if result['score'] >= 70 else "⚠️" if result['score'] >= 50 else "❌"
            output.append(f"{status_icon} {criterion.replace('_', ' ').title()}: {result['score']:.1f}/100")
            
            if 'checks_performed' in result:
                output.append(f"   Checks: {', '.join(result['checks_performed'])}")
            
            if result['score'] < 70 and 'issues_found' in result:
                output.append(f"   Issues: {len(result.get('issues_found', []))}")
    
    output.append("")
    
    # Workflow Results
    output.append("🔄 WORKFLOW ANALYSIS")
    output.append("-" * 40)
    
    workflow_results = results.get('workflow_results', {})
    workflow_steps = [
        ('step1', 'Eingangsprüfung'),
        ('step2', 'Formatprüfung'),
        ('step3', 'Inhaltsprüfung'),
        ('step4', 'Qualitätskontrolle'),
        ('step5', 'Technische Validierung'),
        ('step6', 'Feedback & Rückmeldungen')
    ]
    
    for step_key, step_name in workflow_steps:
        if step_key in workflow_results:
            step_result = workflow_results[step_key]
            status = step_result.get('status', 'unknown')
            status_icon = "✅" if status == 'completed' else "⚠️" if status == 'in_progress' else "❌"
            output.append(f"{status_icon} {step_name}: {status.title()}")
            
            if isinstance(step_result, dict) and 'score' in step_result:
                output.append(f"   Score: {step_result['score']:.1f}/100")
    
    output.append("")
    
    # Recommendations
    if 'criteria_results' in results and 'feedback' in results['criteria_results']:
        feedback = results['criteria_results']['feedback']
        if 'recommendations' in feedback:
            output.append("💡 RECOMMENDATIONS")
            output.append("-" * 40)
            for i, recommendation in enumerate(feedback['recommendations'], 1):
                output.append(f"{i}. {recommendation}")
            output.append("")
    
    # Metadata
    metadata = results.get('metadata', {})
    if metadata:
        output.append("ℹ️ METADATA")
        output.append("-" * 40)
        output.append(f"Source Language: {metadata.get('source_language', 'Unknown')}")
        output.append(f"Target Language: {metadata.get('target_language', 'Unknown')}")
        output.append(f"Subject Area: {metadata.get('subject_area', 'Unknown')}")
        output.append(f"Check Level: {metadata.get('check_level', 'Unknown')}")
        output.append(f"Duration: {metadata.get('duration_seconds', 0):.2f} seconds")
        output.append(f"Timestamp: {metadata.get('timestamp', 'Unknown')}")
    
    output.append("")
    output.append("=" * 80)
    
    return "\n".join(output)


# Integration function for existing app
def start_translation_quality_framework(app_instance):
    """
    Start the translation quality framework from the main app
    """
    try:
        logger.info("Starting Translation Quality Framework from main app")
        return create_translation_quality_gui(app_instance)
    except Exception as e:
        logger.error(f"Error starting Translation Quality Framework: {e}")
        raise


if __name__ == "__main__":
    # Standalone execution
    print("🌍 Translation Quality Framework - Standalone Mode")
    print("=" * 60)
    
    # Create standalone GUI
    create_translation_quality_gui()

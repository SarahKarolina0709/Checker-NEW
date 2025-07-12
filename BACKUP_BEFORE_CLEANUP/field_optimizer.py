# -*- coding: utf-8 -*-
"""
Field-Specific Configuration Optimizer
Enhanced multi-language support with specialized field handling
"""

import json
import os
from typing import Dict, List, Any

class FieldOptimizer:
    def __init__(self):
        self.config_file = "field_configs.json"
        self.field_configs = self._load_field_configs()
        
    def _load_field_configs(self):
        """Load field-specific configurations"""
        default_configs = {
            "medical": {
                "terminology_strictness": "high",
                "consistency_weight": 0.9,
                "specialized_glossaries": ["medical_terms", "pharmaceutical"],
                "critical_sections": ["dosage", "contraindications", "warnings"],
                "language_tool_rules": {
                    "enable": ["MEDICAL_TERMINOLOGY", "PRECISION_LANGUAGE"],
                    "disable": ["COLLOQUIAL_TERMS"]
                },
                "ki_analysis_focus": ["accuracy", "precision", "safety_terms"]
            },
            "legal": {
                "terminology_strictness": "highest",
                "consistency_weight": 0.95,
                "specialized_glossaries": ["legal_terms", "contract_language"],
                "critical_sections": ["definitions", "obligations", "penalties"],
                "language_tool_rules": {
                    "enable": ["LEGAL_TERMINOLOGY", "FORMAL_LANGUAGE"],
                    "disable": ["INFORMAL_LANGUAGE", "CONTRACTIONS"]
                },
                "ki_analysis_focus": ["legal_accuracy", "formal_tone", "binding_language"]
            },
            "technical": {
                "terminology_strictness": "high",
                "consistency_weight": 0.85,
                "specialized_glossaries": ["technical_terms", "engineering"],
                "critical_sections": ["specifications", "procedures", "safety"],
                "language_tool_rules": {
                    "enable": ["TECHNICAL_TERMINOLOGY", "PRECISE_LANGUAGE"],
                    "disable": ["AMBIGUOUS_TERMS"]
                },
                "ki_analysis_focus": ["technical_accuracy", "clarity", "procedure_consistency"]
            },
            "marketing": {
                "terminology_strictness": "medium",
                "consistency_weight": 0.75,
                "specialized_glossaries": ["brand_terms", "marketing_language"],
                "critical_sections": ["brand_names", "calls_to_action", "claims"],
                "language_tool_rules": {
                    "enable": ["BRAND_CONSISTENCY", "PERSUASIVE_LANGUAGE"],
                    "disable": ["OVERLY_FORMAL"]
                },
                "ki_analysis_focus": ["brand_voice", "cultural_adaptation", "persuasive_tone"]
            },
            "financial": {
                "terminology_strictness": "highest",
                "consistency_weight": 0.9,
                "specialized_glossaries": ["financial_terms", "accounting", "investment"],
                "critical_sections": ["figures", "disclaimers", "risk_statements"],
                "language_tool_rules": {
                    "enable": ["FINANCIAL_TERMINOLOGY", "PRECISION_NUMBERS"],
                    "disable": ["APPROXIMATE_LANGUAGE"]
                },
                "ki_analysis_focus": ["numerical_accuracy", "regulatory_compliance", "risk_clarity"]
            },
            "general": {
                "terminology_strictness": "medium",
                "consistency_weight": 0.8,
                "specialized_glossaries": ["general_business"],
                "critical_sections": [],
                "language_tool_rules": {
                    "enable": ["STANDARD_GRAMMAR", "CLARITY"],
                    "disable": []
                },
                "ki_analysis_focus": ["general_quality", "readability", "tone_consistency"]
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_configs = json.load(f)
                    # Merge with defaults
                    for field, config in default_configs.items():
                        if field not in loaded_configs:
                            loaded_configs[field] = config
                    return loaded_configs
        except:
            pass
        
        return default_configs
    
    def get_optimized_checking_config(self, field_type: str, language_pair: str) -> Dict[str, Any]:
        """Get optimized checking configuration for specific field and language pair"""
        field_config = self.field_configs.get(field_type, self.field_configs["general"])
        
        # Language-specific adjustments
        language_adjustments = self._get_language_adjustments(language_pair)
        
        optimized_config = {
            "languagetool": {
                "enabled_rules": field_config["language_tool_rules"]["enable"] + language_adjustments.get("additional_rules", []),
                "disabled_rules": field_config["language_tool_rules"]["disable"],
                "strictness_level": field_config["terminology_strictness"]
            },
            "ki_analysis": {
                "focus_areas": field_config["ki_analysis_focus"],
                "cultural_sensitivity": language_adjustments.get("cultural_sensitivity", "medium"),
                "tone_preferences": language_adjustments.get("tone_preferences", [])
            },
            "consistency_checking": {
                "weight": field_config["consistency_weight"],
                "critical_sections": field_config["critical_sections"],
                "terminology_databases": field_config["specialized_glossaries"]
            },
            "repetition_analysis": {
                "minimum_length": language_adjustments.get("min_phrase_length", 5),
                "similarity_threshold": 0.85,
                "discount_calculation": self._get_discount_rules(field_type)
            }
        }
        
        return optimized_config
    
    def _get_language_adjustments(self, language_pair: str) -> Dict[str, Any]:
        """Get language-specific adjustments"""
        language_configs = {
            "de-DE": {
                "additional_rules": ["COMPOUND_WORDS", "CASE_SENSITIVITY"],
                "cultural_sensitivity": "high",
                "tone_preferences": ["formal", "precise"],
                "min_phrase_length": 6
            },
            "en-US": {
                "additional_rules": ["AMERICAN_SPELLING", "CONCISENESS"],
                "cultural_sensitivity": "medium",
                "tone_preferences": ["clear", "direct"],
                "min_phrase_length": 4
            },
            "fr-FR": {
                "additional_rules": ["FORMAL_PRONOUNS", "GENDER_AGREEMENT"],
                "cultural_sensitivity": "high",
                "tone_preferences": ["formal", "elegant"],
                "min_phrase_length": 5
            },
            "es-ES": {
                "additional_rules": ["FORMAL_ADDRESS", "REGIONAL_VARIANTS"],
                "cultural_sensitivity": "high",
                "tone_preferences": ["formal", "respectful"],
                "min_phrase_length": 5
            },
            "it-IT": {
                "additional_rules": ["FORMAL_PRONOUNS", "REGIONAL_SENSITIVITY"],
                "cultural_sensitivity": "high",
                "tone_preferences": ["formal", "courteous"],
                "min_phrase_length": 5
            }
        }
        
        return language_configs.get(language_pair, {
            "additional_rules": [],
            "cultural_sensitivity": "medium",
            "tone_preferences": ["neutral"],
            "min_phrase_length": 5
        })
    
    def _get_discount_rules(self, field_type: str) -> Dict[str, float]:
        """Get field-specific discount calculation rules"""
        discount_rules = {
            "medical": {
                "exact_match": 0.75,  # Lower discount due to precision needs
                "fuzzy_match": 0.5,
                "minimum_repetitions": 3
            },
            "legal": {
                "exact_match": 0.80,  # Even lower due to legal precision
                "fuzzy_match": 0.40,
                "minimum_repetitions": 2
            },
            "technical": {
                "exact_match": 0.70,
                "fuzzy_match": 0.50,
                "minimum_repetitions": 3
            },
            "marketing": {
                "exact_match": 0.60,  # Higher discount possible
                "fuzzy_match": 0.70,
                "minimum_repetitions": 2
            },
            "financial": {
                "exact_match": 0.75,
                "fuzzy_match": 0.45,
                "minimum_repetitions": 3
            },
            "general": {
                "exact_match": 0.65,
                "fuzzy_match": 0.60,
                "minimum_repetitions": 2
            }
        }
        
        return discount_rules.get(field_type, discount_rules["general"])
    
    def optimize_workflow_sequence(self, field_type: str, quality_level: str) -> List[str]:
        """Get optimized workflow sequence for field type and quality level"""
        base_sequence = ["file_analysis", "languagetool", "consistency_check"]
        
        if quality_level in ["v1", "comprehensive"]:
            field_specific = {
                "medical": ["terminology_check", "ki_safety_analysis", "regulatory_compliance"],
                "legal": ["legal_terminology", "ki_formal_analysis", "binding_language_check"],
                "technical": ["technical_terminology", "ki_accuracy_analysis", "procedure_validation"],
                "marketing": ["brand_consistency", "ki_cultural_analysis", "tone_optimization"],
                "financial": ["numerical_accuracy", "ki_compliance_analysis", "risk_assessment"],
                "general": ["ki_general_analysis", "readability_check"]
            }
            
            base_sequence.extend(field_specific.get(field_type, field_specific["general"]))
        
        base_sequence.append("report_generation")
        return base_sequence
    
    def save_field_configs(self):
        """Save current field configurations"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.field_configs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving field configs: {e}")

# Global instance
field_optimizer = FieldOptimizer()

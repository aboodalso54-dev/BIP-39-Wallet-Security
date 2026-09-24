"""DevForge 2.0 - First-of-its-kind Intelligent Development Environment.

A revolutionary platform that orchestrates all dev tools, analyzes errors,
predicts bugs, translates code, and auto-fixes issues to make the impossible possible.
"""

__version__ = "2.0.0"
__author__ = "DevForge Team"
__description__ = "Intelligent Development Environment - Making the Impossible Possible"

from devforge.predictive_engine import PredictiveErrorEngine
from devforge.code_translator import UniversalCodeTranslator
from devforge.self_healing_pipeline import SelfHealingPipeline
from devforge.ai_generator import AICodeGenerator
from devforge.dependency_resolver import SmartDependencyResolver
from devforge.config import DevForgeConfig

__all__ = [
    "PredictiveErrorEngine",
    "UniversalCodeTranslator",
    "SelfHealingPipeline",
    "AICodeGenerator",
    "SmartDependencyResolver",
    "DevForgeConfig",
]

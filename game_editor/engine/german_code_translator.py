"""
Deutscher Code-Translator - Übersetzt deutschen Code in Python

Übersetzt deutsche Schlüsselwörter (definiere, wenn, für, etc.) in Python-Schlüsselwörter.
"""
import re
from typing import Tuple, Dict, List


# Python-Schlüsselwörter (für Validierung)
PYTHON_KEYWORDS = {
    "def", "class", "if", "else", "elif", "for", "while",
    "return", "True", "False", "None", "and", "or", "not",
    "import", "from", "as", "pass", "break", "continue",
    "try", "except", "finally", "raise", "with", "lambda",
    "is", "in", "del", "global", "nonlocal", "yield"
}

# Mapping: Deutsch → Python (beide Varianten: mit und ohne Umlaute)
GERMAN_TO_PYTHON = {
    # Schlüsselwörter (mit Umlauten)
    "definiere": "def",
    "funktion": "def",  # Alte Variante - wird auch unterstützt für Rückwärtskompatibilität
    "wenn": "if",
    "sonst": "else",
    "sonst_wenn": "elif",
    "für": "for",
    "während": "while",
    "gib_zurück": "return",
    "gib_zurueck": "return",  # Ohne Umlaut
    "überspringen": "pass",
    "ueberspringen": "pass",  # Ohne Umlaut
    "breche": "break",
    "mache_weiter": "continue",
    "versuche": "try",
    "außer": "except",
    "ausser": "except",  # Ohne Umlaut
    "schließlich": "finally",
    "schliesslich": "finally",  # Ohne Umlaut
    "importiere": "import",
    "von": "from",
    "als": "as",
    "global": "global",
    "wahr": "True",
    "falsch": "False",
    "keine": "None",
    "und": "and",
    "oder": "or",
    "nicht": "not",
    "ist": "is",
    "in": "in",
    "mit": "with",
}

# Mapping: Deutsche API-Funktionen → Englische API-Funktionen
GERMAN_API_TO_ENGLISH = {
    "hole_objekt": "get_object",
    "hole_alle_objekte": "get_all_objects",
    "taste_gedrückt": "key_pressed",
    "taste_runter": "key_down",
    "maus_position": "mouse_position",
    "drucke_debug": "print_debug",
    "erstelle_objekt": "spawn_object",
    "bewege_mit_kollision": "move_with_collision",
    "drücke_objekte": "push_objects",
    "fixiere_y_position": "lock_y_position",
    "entferne_y_fixierung": "unlock_y_position",
    # GameObject-Methoden
    "kollidiert_mit": "collides_with",
    "zerstöre": "destroy",
}

# Reverse-Mapping: Englische API-Funktionen → Deutsche API-Funktionen
ENGLISH_API_TO_GERMAN = {v: k for k, v in GERMAN_API_TO_ENGLISH.items()}


def detect_code_language(code: str) -> str:
    """
    Erkennt automatisch die Sprache des Codes anhand von Schlüsselwörtern
    
    Args:
        code: Code zum Analysieren
        
    Returns:
        "deutsch" oder "englisch" (Standard: "deutsch" wenn unklar)
    """
    if not code or not code.strip():
        return "deutsch"  # Standard
    
    # Strings maskieren, damit Schlüsselwörter in Strings nicht gezählt werden
    string_pattern = r'"[^"]*"|\'[^\']*\''
    masked_code = re.sub(string_pattern, "__STRING__", code)
    
    # Zähle deutsche und englische Schlüsselwörter
    german_count = 0
    english_count = 0
    
    # Deutsche Schlüsselwörter zählen
    for german_keyword in GERMAN_TO_PYTHON.keys():
        # Überspringe gemeinsame Keywords
        if german_keyword in {"in", "global"}:
            continue
        pattern = r'\b' + re.escape(german_keyword) + r'\b'
        matches = len(re.findall(pattern, masked_code))
        german_count += matches
    
    # Englische Schlüsselwörter zählen
    for english_keyword in PYTHON_KEYWORDS:
        # Überspringe gemeinsame Keywords
        if english_keyword in {"in", "global"}:
            continue
        # Überspringe Keywords die auch in GERMAN_TO_PYTHON.values() vorkommen
        # (weil die schon übersetzt sein könnten)
        pattern = r'\b' + re.escape(english_keyword) + r'\b'
        matches = len(re.findall(pattern, masked_code))
        english_count += matches
    
    # Entscheidung: Welche Sprache dominiert?
    if german_count > english_count:
        return "deutsch"
    elif english_count > german_count:
        return "englisch"
    else:
        # Gleichstand oder kein Keyword gefunden: Standard ist Deutsch
        return "deutsch"


def validate_code_language(code: str, expected_language: str) -> Tuple[bool, str, int]:
    """
    Validiert ob Code die erwartete Sprache verwendet
    
    Args:
        code: Code zum Validieren
        expected_language: "deutsch" oder "englisch"
        
    Returns:
        Tuple (is_valid, error_message, error_line)
        - is_valid: True wenn Code die richtige Sprache verwendet
        - error_message: Fehlermeldung wenn falsch
        - error_line: Zeile mit Fehler (0 wenn kein Fehler)
    """
    if not code or not code.strip():
        return True, "", 0
    
    # Schlüsselwörter die in beiden Sprachen gleich sind (nicht validieren)
    # "in", "global" sind in beiden Sprachen gleich
    common_keywords = {"in", "global"}
    
    if expected_language == "deutsch":
        # Code sollte deutsche Schlüsselwörter verwenden
        # Fehler wenn englische Schlüsselwörter gefunden werden
        lines = code.split('\n')
        for line_num, line in enumerate(lines, start=1):
            # Strings maskieren
            string_pattern = r'"[^"]*"|\'[^\']*\''
            masked_line = re.sub(string_pattern, "__STRING__", line)
            
            # Prüfe auf englische Schlüsselwörter (außer gemeinsame)
            for keyword in PYTHON_KEYWORDS:
                if keyword in common_keywords:
                    continue  # Überspringen
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, masked_line):
                    return False, f"Englisches Schlüsselwort '{keyword}' gefunden. Bitte verwende die deutsche Version.", line_num
        
        return True, "", 0
    
    elif expected_language == "englisch":
        # Code sollte englische Schlüsselwörter verwenden
        # Fehler wenn deutsche Schlüsselwörter gefunden werden
        lines = code.split('\n')
        for line_num, line in enumerate(lines, start=1):
            # Strings maskieren
            string_pattern = r'"[^"]*"|\'[^\']*\''
            masked_line = re.sub(string_pattern, "__STRING__", line)
            
            # Prüfe auf deutsche Schlüsselwörter (außer gemeinsame)
            for german_keyword in GERMAN_TO_PYTHON.keys():
                if german_keyword in common_keywords:
                    continue  # Überspringen
                pattern = r'\b' + re.escape(german_keyword) + r'\b'
                if re.search(pattern, masked_line):
                    return False, f"Deutsches Schlüsselwort '{german_keyword}' gefunden. Bitte verwende die englische Version.", line_num
        
        return True, "", 0
    
    return True, "", 0  # Unbekannte Sprache = keine Validierung


def translate_code(german_code: str, validate_language: bool = False, expected_language: str = "deutsch") -> Tuple[str, Dict[int, int], Tuple[bool, str, int]]:
    """
    Übersetzt deutschen Code in Python-Code
    
    Args:
        german_code: Code mit deutschen Schlüsselwörtern
        validate_language: Wenn True, wird geprüft ob Code die richtige Sprache verwendet
        expected_language: "deutsch" oder "englisch" (für Validierung)
        
    Returns:
        Tuple (python_code, line_mapping, validation_result)
        - python_code: Übersetzter Python-Code (oder original wenn englisch)
        - line_mapping: Mapping von Python-Zeile → Deutsch-Zeile
        - validation_result: Tuple (is_valid, error_message, error_line)
    
    WICHTIG: Strings werden maskiert und bleiben unverändert!
    """
    # Validierung (wenn aktiviert)
    validation_result = (True, "", 0)
    if validate_language:
        validation_result = validate_code_language(german_code, expected_language)
        if not validation_result[0]:
            # Fehler: Falsche Sprache - Code nicht übersetzen
            return german_code, {}, validation_result
    
    if not german_code or not german_code.strip():
        return german_code, {}, validation_result
    
    # Wenn Englisch erwartet wird, Code nicht übersetzen
    if expected_language == "englisch":
        line_mapping = {}
        num_lines = len(german_code.split('\n'))
        for i in range(1, num_lines + 1):
            line_mapping[i] = i
        return german_code, line_mapping, validation_result
    
    # Strings maskieren (damit sie nicht übersetzt werden)
    # Global für gesamten Code
    string_map = {}
    string_counter = 0
    
    def mask_strings(text: str) -> str:
        """Maskiert Strings in einem Text"""
        nonlocal string_counter, string_map
        
        # Pattern für Strings: Triple quotes, double quotes, single quotes
        # Reihenfolge wichtig: Triple quotes zuerst (mehrere Zeilen)
        # Single/Double quotes (eine Zeile)
        patterns = [
            (r'"""[\s\S]*?"""'),  # Triple double quotes (mehrere Zeilen)
            (r"'''[\s\S]*?'''"),  # Triple single quotes (mehrere Zeilen)
            (r'"[^"\\]*(\\.[^"\\]*)*"'),  # Double quotes (mit Escapes)
            (r"'[^'\\]*(\\.[^'\\]*)*'"),  # Single quotes (mit Escapes)
        ]
        
        for pattern in patterns:
            def replace_match(match):
                nonlocal string_counter
                original = match.group(0)
                placeholder = f"__STRING_{string_counter}__"
                string_map[placeholder] = original
                string_counter += 1
                return placeholder
            
            text = re.sub(pattern, replace_match, text)
        
        return text
    
    def unmask_strings(text: str) -> str:
        """Demaskiert Strings in einem Text"""
        # In umgekehrter Reihenfolge ersetzen (größere Platzhalter zuerst)
        sorted_placeholders = sorted(string_map.keys(), key=len, reverse=True)
        for placeholder in sorted_placeholders:
            original = string_map[placeholder]
            text = text.replace(placeholder, original)
        return text
    
    # Schritt 1: Strings maskieren (über gesamten Code)
    masked_code = mask_strings(german_code)
    
    # Schritt 2: Deutsche Schlüsselwörter übersetzen (nur ganze Wörter!)
    python_code = masked_code
    for german, python in GERMAN_TO_PYTHON.items():
        # Nur ganze Wörter ersetzen (mit Wort-Grenzen)
        pattern = r'\b' + re.escape(german) + r'\b'
        python_code = re.sub(pattern, python, python_code)
    
    # Schritt 2b: Deutsche API-Funktionen übersetzen (nur ganze Wörter!)
    # WICHTIG: Muss nach Keywords passieren, damit "mit" nicht übersetzt wird wenn es Teil von "bewege_mit_kollision" ist
    for german_func, english_func in GERMAN_API_TO_ENGLISH.items():
        # Nur ganze Wörter ersetzen (mit Wort-Grenzen)
        pattern = r'\b' + re.escape(german_func) + r'\b'
        python_code = re.sub(pattern, english_func, python_code)
    
    # Schritt 3: Strings demaskieren
    python_code = unmask_strings(python_code)
    
    # Zeile-Mapping: Python-Zeile → Deutsch-Zeile (1:1 Mapping, da Zeilenanzahl gleich bleibt)
    # Für Fehlermeldungen: Python-Zeile = Deutsch-Zeile (gleiche Nummer)
    line_mapping = {}
    num_lines = len(python_code.split('\n'))
    for i in range(1, num_lines + 1):
        line_mapping[i] = i
    
    return python_code, line_mapping, validation_result


# Reverse-Mapping: Python → Deutsch (für Rückübersetzung)
PYTHON_TO_GERMAN = {}
# Für mehrdeutige Mappings (z.B. "gib_zurueck" und "gib_zurück" beide → "return")
# Verwende die bevorzugte Version als Standard
for german, python in GERMAN_TO_PYTHON.items():
    if python not in PYTHON_TO_GERMAN:
        PYTHON_TO_GERMAN[python] = german
    # Wenn beide Versionen existieren, bevorzuge "definiere" über "funktion"
    elif python == "def" and german == "definiere":
        PYTHON_TO_GERMAN[python] = german  # "definiere" hat Vorrang
    # Wenn beide Versionen existieren, bevorzuge die mit Umlaut
    elif 'ü' in german or 'ä' in german or 'ö' in german:
        PYTHON_TO_GERMAN[python] = german


def translate_code_reverse(python_code: str, target_language: str) -> Tuple[str, bool, str]:
    """
    Übersetzt Python-Code zurück in deutsche oder englische Schlüsselwörter
    
    Args:
        python_code: Python-Code mit englischen Schlüsselwörtern
        target_language: "deutsch" oder "englisch"
        
    Returns:
        Tuple (translated_code, success, error_message)
        - translated_code: Übersetzter Code (oder original bei Fehler)
        - success: True wenn Übersetzung erfolgreich war
        - error_message: Fehlermeldung wenn Übersetzung nicht vollständig möglich
    """
    if not python_code or not python_code.strip():
        return python_code, True, ""
    
    if target_language == "englisch":
        # Zurück zu Englisch: Code bleibt wie er ist (ist bereits Englisch)
        return python_code, True, ""
    
    if target_language != "deutsch":
        return python_code, False, f"Unbekannte Zielsprache: {target_language}"
    
    # Übersetzen von Python zu Deutsch
    # Strings maskieren (damit sie nicht übersetzt werden)
    string_map = {}
    string_counter = 0
    
    def mask_strings(text: str) -> str:
        """Maskiert Strings in einem Text"""
        nonlocal string_counter, string_map
        
        patterns = [
            (r'"""[\s\S]*?"""'),  # Triple double quotes
            (r"'''[\s\S]*?'''"),  # Triple single quotes
            (r'"[^"\\]*(\\.[^"\\]*)*"'),  # Double quotes
            (r"'[^'\\]*(\\.[^'\\]*)*'"),  # Single quotes
        ]
        
        for pattern in patterns:
            def replace_match(match):
                nonlocal string_counter
                original = match.group(0)
                placeholder = f"__STRING_{string_counter}__"
                string_map[placeholder] = original
                string_counter += 1
                return placeholder
            
            text = re.sub(pattern, replace_match, text)
        
        return text
    
    def unmask_strings(text: str) -> str:
        """Demaskiert Strings in einem Text"""
        sorted_placeholders = sorted(string_map.keys(), key=len, reverse=True)
        for placeholder in sorted_placeholders:
            original = string_map[placeholder]
            text = text.replace(placeholder, original)
        return text
    
    # Schritt 1: Strings maskieren
    masked_code = mask_strings(python_code)
    
    # Schritt 2: Python-Schlüsselwörter in deutsche übersetzen
    german_code = masked_code
    untranslatable_keywords = []
    
    # Prüfe ob alle Keywords übersetzbar sind
    for python_keyword in PYTHON_KEYWORDS:
        # Überspringe gemeinsame Keywords
        if python_keyword in {"in", "global"}:
            continue
        pattern = r'\b' + re.escape(python_keyword) + r'\b'
        if re.search(pattern, masked_code):
            if python_keyword not in PYTHON_TO_GERMAN:
                untranslatable_keywords.append(python_keyword)
    
    # Wenn nicht alle Keywords übersetzbar sind, Fehler zurückgeben
    if untranslatable_keywords:
        error_msg = f"Vollständige Übersetzung nicht möglich. Nicht übersetzbare Schlüsselwörter: {', '.join(untranslatable_keywords)}"
        return python_code, False, error_msg
    
    # Übersetzen: Zuerst Keywords
    for python, german in PYTHON_TO_GERMAN.items():
        # Überspringe gemeinsame Keywords
        if python in {"in", "global"}:
            continue
        pattern = r'\b' + re.escape(python) + r'\b'
        german_code = re.sub(pattern, german, german_code)
    
    # Schritt 2b: Englische API-Funktionen in deutsche übersetzen
    # WICHTIG: Muss nach Keywords passieren, damit "with" nicht übersetzt wird wenn es Teil von "move_with_collision" ist
    for english_func, german_func in ENGLISH_API_TO_GERMAN.items():
        # Nur ganze Wörter ersetzen (mit Wort-Grenzen)
        pattern = r'\b' + re.escape(english_func) + r'\b'
        german_code = re.sub(pattern, german_func, german_code)
    
    # Schritt 3: Strings demaskieren
    german_code = unmask_strings(german_code)
    
    return german_code, True, ""

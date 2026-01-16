"""
Syntax Highlighter - Syntax-Highlighting via LSP
"""
from PySide6.QtGui import QTextCharFormat, QColor, QTextDocument
from PySide6.QtCore import QObject, Signal
from typing import Dict, List, Any
import re


class LSPSyntaxHighlighter(QObject):
    """Syntax-Highlighting basierend auf LSP-Token-Informationen"""
    
    def __init__(self, document: QTextDocument, parent=None):
        super().__init__(parent)
        self.document = document
        self.formats: Dict[str, QTextCharFormat] = {}
        self.default_text_color = QColor(212, 212, 212)  # Standard-Textfarbe (kann über Einstellungen geändert werden)
        self._last_formatted_text = None  # Cache des zuletzt formatierten Textes
        self._setup_formats()
    
    def _setup_formats(self):
        """Erstellt Format-Objekte für verschiedene Token-Typen"""
        # Keywords (Python) - Stärkeres Blau
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(79, 175, 239))  # Kräftiges Blau
        keyword_format.setFontWeight(600)
        self.formats["keyword"] = keyword_format
        
        # Strings - Stärkeres Orange
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(236, 118, 0))  # Kräftiges Orange
        self.formats["string"] = string_format
        
        # Kommentare - Dunkelgrau
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(100, 100, 100))  # Dunkelgrau
        comment_format.setFontItalic(True)
        self.formats["comment"] = comment_format
        
        # Zahlen - Stärkeres Grün
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))  # Grün
        self.formats["number"] = number_format
        
        # Funktionen - Stärkeres Gelb
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 220, 100))  # Kräftiges Gelb
        self.formats["function"] = function_format
        
        # Klassen - Stärkeres Türkis
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(78, 201, 176))  # Türkis
        self.formats["class"] = class_format
        
        # Variablen - Hellblau
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor(156, 220, 254))  # Hellblau
        self.formats["variable"] = variable_format
        
        # Operatoren und Zeichen - Kräftiges Cyan
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor(180, 180, 255))  # Kräftiges Cyan/Lila
        self.formats["operator"] = operator_format
    
    def apply_syntax_highlighting(self, text: str):
        """Wendet Syntax-Highlighting auf den Text an (einfache Regex-basierte Version)"""
        from PySide6.QtGui import QTextCursor
        
        # WICHTIG: Verhindere Flackern - prüfe ob Text sich geändert hat UND ob Dokument formatiert ist
        text_unchanged = (self._last_formatted_text == text)
        
        # Prüfe ob Dokument bereits formatiert ist (hat Formatierungen, nicht nur Standard-Textfarbe)
        document_formatted = False
        if text_unchanged and len(text) > 0:
            # Prüfe mehrere Positionen im Dokument auf Formatierungen
            # Suche nach Strings, Kommentaren, Keywords, etc. die bereits formatiert sind
            cursor = QTextCursor(self.document)
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            
            # Prüfe mehrere Stellen: Anfang, Mitte (wenn lang genug), Ende
            check_positions = [0]
            if len(text) > 100:
                check_positions.append(len(text) // 2)
            if len(text) > 50:
                check_positions.append(min(100, len(text) - 1))
            
            for pos in check_positions:
                if pos >= len(text):
                    continue
                cursor.setPosition(pos)
                char_format = cursor.charFormat()
                if char_format.hasProperty(QTextCharFormat.Property.ForegroundBrush):
                    color = char_format.foreground().color()
                    # Wenn Farbe nicht Standard-Textfarbe ist, ist Dokument formatiert
                    if color != self.default_text_color:
                        document_formatted = True
                        break
        
        # Nur überspringen wenn Text gleich ist UND Dokument bereits formatiert ist
        if text_unchanged and document_formatted:
            # Text hat sich nicht geändert und Dokument ist bereits formatiert
            # Kein Highlighting nötig (verhindert Flackern)
            return
        
        # Text hat sich geändert ODER Dokument ist nicht formatiert - Highlighting ausführen
        self._last_formatted_text = text
        
        # Blockiere Signals während des Highlightings, um rekursive Aufrufe zu vermeiden
        self.document.blockSignals(True)
        try:
            # Standard-Format zurücksetzen (verwendet die Standard-Textfarbe aus Einstellungen)
            cursor = QTextCursor(self.document)
            cursor.select(QTextCursor.SelectionType.Document)
            default_format = cursor.charFormat()
            default_format.setForeground(self.default_text_color)  # Standard-Textfarbe aus Einstellungen
            cursor.setCharFormat(default_format)
            
            # Strings (einfache und doppelte Anführungszeichen) - ZUERST, damit Operatoren in Strings nicht formatiert werden
            string_patterns = [
                (r'""".*?"""', re.DOTALL),  # Triple double quotes
                (r"'''.*?'''", re.DOTALL),  # Triple single quotes
                (r'"[^"]*"', 0),  # Doppelte Anführungszeichen
                (r"'[^']*'", 0),  # Einfache Anführungszeichen
            ]
            
            # Speichere String-Bereiche, um Operatoren darin zu ignorieren
            string_ranges = []
            string_count = 0
            for pattern, flags in string_patterns:
                for match in re.finditer(pattern, text, flags):
                    start = match.start()
                    end = match.end()
                    string_ranges.append((start, end))
                    cursor.setPosition(start)
                    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                    cursor.setCharFormat(self.formats["string"])
                    string_count += 1
            
            # Kommentare - ZUERST, damit Operatoren in Kommentaren nicht formatiert werden
            comment_pattern = r'#.*$'
            comment_ranges = []
            comment_count = 0
            for match in re.finditer(comment_pattern, text, re.MULTILINE):
                start = match.start()
                end = match.end()
                comment_ranges.append((start, end))
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(self.formats["comment"])
                comment_count += 1
            
            # Hilfsfunktion: Prüft ob Position in String oder Kommentar
            # WICHTIG: Muss NACH string_ranges und comment_ranges definiert werden!
            def is_in_string_or_comment(pos):
                for start, end in string_ranges + comment_ranges:
                    if start <= pos < end:
                        return True
                return False
            
            # Python Keywords (englisch)
            english_keywords = [
                "def", "class", "if", "else", "elif", "for", "while",
                "return", "True", "False", "None", "and", "or", "not",
                "import", "from", "as", "pass", "break", "continue",
                "try", "except", "finally", "raise", "with", "lambda",
                "is", "in", "del", "global", "nonlocal", "yield"
            ]
            
            # Deutsche Keywords (werden genauso hervorgehoben wie englische)
            german_keywords = [
                "definiere", "funktion", "wenn", "sonst", "sonst_wenn", "fuer", "für",
                "waehrend", "während", "gib_zurueck", "gib_zurück",
                "ueberspringen", "überspringen", "breche", "mache_weiter",
                "versuche", "ausser", "außer", "schliesslich", "schließlich",
                "importiere", "von", "als", "global", "wahr", "falsch",
                "keine", "und", "oder", "nicht", "ist", "in", "mit"
            ]
            
            # Alle Keywords hervorheben (deutsch + englisch)
            all_keywords = english_keywords + german_keywords
            
            # Keywords hervorheben
            for keyword in all_keywords:
                pattern = rf'\b{re.escape(keyword)}\b'
                for match in re.finditer(pattern, text):
                    start = match.start()
                    end = match.end()
                    # Prüfe ob nicht in String oder Kommentar
                    if not is_in_string_or_comment(start):
                        cursor.setPosition(start)
                        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                        cursor.setCharFormat(self.formats["keyword"])
            
            # Zahlen
            number_pattern = r'\b\d+\.?\d*\b'
            for match in re.finditer(number_pattern, text):
                start = match.start()
                end = match.end()
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(self.formats["number"])
            
            # Funktionen (def function_name, definiere function_name oder funktion function_name)
            function_patterns = [
                r'\bdef\s+(\w+)\s*\(',  # Englisch: def function_name(
                r'\bdefiniere\s+(\w+)\s*\(',  # Deutsch: definiere function_name(
                r'\bfunktion\s+(\w+)\s*\(',  # Deutsch (alt): funktion function_name(
            ]
            
            for function_pattern in function_patterns:
                for match in re.finditer(function_pattern, text):
                    func_start = match.end(1) - len(match.group(1))
                    func_end = match.end(1)
                    # Prüfe ob nicht in String oder Kommentar
                    if not is_in_string_or_comment(func_start):
                        cursor.setPosition(func_start)
                        cursor.setPosition(func_end, QTextCursor.MoveMode.KeepAnchor)
                        cursor.setCharFormat(self.formats["function"])
            
            # Klassen (class ClassName)
            class_pattern = r'\bclass\s+(\w+)'
            for match in re.finditer(class_pattern, text):
                class_start = match.end(1) - len(match.group(1))
                class_end = match.end(1)
                # Prüfe ob nicht in String oder Kommentar
                if not is_in_string_or_comment(class_start):
                    cursor.setPosition(class_start)
                    cursor.setPosition(class_end, QTextCursor.MoveMode.KeepAnchor)
                    cursor.setCharFormat(self.formats["class"])
            
            # Operatoren und Zeichen (+, -, *, /, =, ==, !=, <, >, <=, >=, :, ., ,, ;, etc.)
            # ZULETZT formatieren, damit sie nicht von anderen Formatierungen überschrieben werden
            # WICHTIG: Zuerst mehrstellige Operatoren (==, !=, <=, >=, //, **), dann einzelne
            multi_operators = [r'==', r'!=', r'<=', r'>=', r'//', r'\*\*']
            for op_pattern in multi_operators:
                for match in re.finditer(op_pattern, text):
                    start = match.start()
                    end = match.end()
                    # Nur formatieren wenn nicht in String oder Kommentar
                    if not is_in_string_or_comment(start):
                        cursor.setPosition(start)
                        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                        cursor.setCharFormat(self.formats["operator"])
            
            # Einzelne Operatoren und Zeichen
            single_operators = r'[+\-*/=<>!:.,;()\[\]{}]'
            for match in re.finditer(single_operators, text):
                start = match.start()
                end = match.end()
                # Nur formatieren wenn nicht in String oder Kommentar
                if not is_in_string_or_comment(start):
                    cursor.setPosition(start)
                    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                    cursor.setCharFormat(self.formats["operator"])
        finally:
            # Signals wieder aktivieren
            self.document.blockSignals(False)
    
    def update_formats(self, formats: dict):
        """Aktualisiert die Format-Objekte (für Einstellungen)"""
        for key, color_hex in formats.items():
            if key == "default":
                # Standard-Textfarbe aktualisieren
                color = QColor(color_hex)
                if color.isValid():
                    self.default_text_color = color
            elif key in self.formats:
                # Hex-String zu QColor konvertieren
                color = QColor(color_hex)
                if color.isValid():
                    self.formats[key].setForeground(color)
        
        # Cache zurücksetzen, damit Highlighting neu angewendet wird (bei Farbänderungen)
        self._last_formatted_text = None
    
    def reset_cache(self):
        """Setzt den Cache zurück (z.B. beim Laden von neuem Code)"""
        self._last_formatted_text = None

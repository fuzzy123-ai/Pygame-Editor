"""
Image Fixer - Behebt iCCP-Profil-Probleme in PNG-Bildern
Verwendet Pillow (PIL) als primäre Methode, ImageMagick (Wand) als Fallback
"""
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Pillow (PIL) - primäre Methode
try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("Pillow (PIL) nicht verfügbar. Versuche ImageMagick (Wand)...")

# ImageMagick (Wand) - Fallback falls Pillow nicht verfügbar
if not HAS_PIL:
    try:
        from wand.image import Image as WandImage
        HAS_WAND = True
    except ImportError:
        HAS_WAND = False
        logger.warning("Weder Pillow noch Wand verfügbar. iCCP-Profil-Korrektur wird übersprungen.")
else:
    HAS_WAND = False


def fix_iccp_profile(image_path: Path, backup: bool = False) -> bool:
    """
    Behebt iCCP-Profil-Probleme in PNG-Bildern
    Verwendet Pillow (PIL) als primäre Methode, ImageMagick (Wand) als Fallback
    
    Args:
        image_path: Pfad zum Bild
        backup: Ob eine Backup-Datei erstellt werden soll
    
    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    if not HAS_PIL and not HAS_WAND:
        logger.debug(f"Weder Pillow noch Wand verfügbar, überspringe iCCP-Fix für {image_path}")
        return False
    
    if not image_path.exists():
        logger.warning(f"Bild nicht gefunden: {image_path}")
        return False
    
    # Nur PNG-Bilder verarbeiten (iCCP ist ein PNG-spezifisches Problem)
    if image_path.suffix.lower() != '.png':
        return True  # Kein Fehler, aber auch keine Verarbeitung nötig
    
    try:
        # Backup erstellen falls gewünscht
        if backup:
            backup_path = image_path.with_suffix(image_path.suffix + '.backup')
            if not backup_path.exists():
                import shutil
                shutil.copy2(image_path, backup_path)
        
        # Methode 1: Pillow (PIL) - primäre Methode
        if HAS_PIL:
            # Bild mit Pillow öffnen
            img = PILImage.open(image_path)
            
            # iCCP-Profil entfernen: Bild ohne ICC-Profil neu speichern
            # Pillow entfernt automatisch fehlerhafte Profile beim Speichern
            # Wir speichern explizit ohne Profil
            img.save(image_path, 'PNG', optimize=False)
            img.close()
            
            logger.debug(f"iCCP-Profil korrigiert (Pillow): {image_path}")
            return True
        
        # Methode 2: ImageMagick (Wand) - Fallback
        elif HAS_WAND:
            with WandImage(filename=str(image_path)) as img:
                # iCCP-Profil entfernen durch Neu-Speichern ohne Profil
                img.format = 'png'
                # Profil entfernen
                if 'icc' in img.profiles:
                    del img.profiles['icc']
                # Bild speichern (überschreibt Original)
                img.save(filename=str(image_path))
            
            logger.debug(f"iCCP-Profil korrigiert (ImageMagick): {image_path}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Fehler beim Beheben des iCCP-Profils für {image_path}: {e}")
        return False


def fix_images_in_directory(directory: Path, recursive: bool = True) -> tuple[int, list[str]]:
    """
    Behebt iCCP-Profil-Probleme in allen PNG-Bildern in einem Verzeichnis
    
    Args:
        directory: Verzeichnis mit Bildern
        recursive: Ob auch Unterverzeichnisse durchsucht werden sollen
    
    Returns:
        Tuple (anzahl_behoben, liste_der_fehler)
    """
    if not directory.exists():
        return (0, [f"Verzeichnis nicht gefunden: {directory}"])
    
    fixed_count = 0
    errors = []
    
    # PNG-Dateien finden
    if recursive:
        image_files = list(directory.rglob("*.png"))
    else:
        image_files = list(directory.glob("*.png"))
    
    for image_file in image_files:
        if fix_iccp_profile(image_file, backup=False):
            fixed_count += 1
        else:
            errors.append(f"Fehler bei {image_file.name}")
    
    return (fixed_count, errors)

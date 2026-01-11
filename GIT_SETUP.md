# Git Repository Setup - Anleitung

Das lokale Git-Repository wurde erfolgreich initialisiert und der erste Commit wurde erstellt.

## Nächste Schritte: Remote-Repository erstellen und hochladen

### Option 1: GitHub (empfohlen)

1. **Repository auf GitHub erstellen:**
   - Gehe zu https://github.com/new
   - Repository-Name: z.B. `pygame-editor` oder `gamedev-edu-editor`
   - **WICHTIG:** Lass das Repository **LEER** (keine README, keine .gitignore, keine Lizenz)
   - Klicke auf "Create repository"

2. **Remote hinzufügen und hochladen:**
   ```bash
   git remote add origin https://github.com/DEIN-USERNAME/REPOSITORY-NAME.git
   git branch -M main
   git push -u origin main
   ```

### Option 2: GitLab

1. **Repository auf GitLab erstellen:**
   - Gehe zu https://gitlab.com/projects/new
   - Repository-Name: z.B. `pygame-editor`
   - **WICHTIG:** Lass das Repository **LEER**
   - Klicke auf "Create project"

2. **Remote hinzufügen und hochladen:**
   ```bash
   git remote add origin https://gitlab.com/DEIN-USERNAME/REPOSITORY-NAME.git
   git branch -M main
   git push -u origin main
   ```

### Option 3: Andere Git-Hosting-Dienste

Ähnliche Schritte für andere Dienste (Bitbucket, etc.)

## Aktueller Status

- ✅ Git Repository initialisiert
- ✅ .gitignore erstellt
- ✅ Initialer Commit erstellt (80 Dateien, 9344 Zeilen)
- ⏳ Remote-Repository muss noch erstellt und verbunden werden

## Nützliche Git-Befehle

```bash
# Status prüfen
git status

# Änderungen anzeigen
git diff

# Neuen Commit erstellen
git add .
git commit -m "Beschreibung der Änderungen"

# Zum Remote-Repository pushen
git push

# Vom Remote-Repository pullen
git pull
```

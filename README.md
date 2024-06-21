# Einsatz und Anpassung generativer Sprachmodelle für eine effektive Lernunterstützung

Dieses Repository enthält den Backend-Code für die Entwicklung eines Chatbots.

## Hosting
- Die Anwendung wird über [PythonAnywhere](https://www.pythonanywhere.com/) gehostet.

## Frontend
- Das Frontend wurde mit Voiceflow erstellt und kann über folgenden Link geklont werden: [Voiceflow-Projekt](https://creator.voiceflow.com/dashboard?import=66758c370d33ccc116268bbb).

## Projektstruktur und Code
### `main.py`
- Enthält die Routen der Flask-Anwendung, welche über API-Aufrufe mit Voiceflow kommunizieren.

### `functions.py`
- Beinhaltet Hilfsfunktionen für die einzelnen Routen und Use Cases.

### `instructions.py`
- Enthält die Anweisungen für die Assistants der verschiedenen Use Cases.

### `Datasource` Verzeichnis
- Enthält die Datenbasis (Files) für das Knowledge Retrieval der Assistants.

### `create_assistant` Verzeichnis
- Enthält die Logik zur Erstellung eines Assistants.

### `finetuning` Verzeichnis
- Beinhaltet die Logik zur Erstellung eines Fine-Tuning-Jobs und zum Testen des feinabgestimmten Modells.

## Architekturdiagramm  
![architecture (1)](https://github.com/ZoeSuam/BA2024_tutorbot/assets/92214462/382a6d72-7bb2-40fd-9b7a-128f1fecedd2)





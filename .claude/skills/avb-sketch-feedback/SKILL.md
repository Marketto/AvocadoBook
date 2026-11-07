---
name: avb-sketch-feedback
description: Far indicare all'utente un punto o una forma disegnando su un'immagine (anteprima, sezione) in una pagina artifact, e leggere il disegno inviato. Usala quando l'utente non riesce a spiegare a parole quale zona o forma intende.
---
# Disegno dell'utente su un'immagine

1. Prepara l'immagine (es. `python3 tools/render.py section` → sezione con i pezzi colorati).
2. `python3 tools/make_editor.py <immagine.png> build/editor/segna.html`.
3. Pubblica con il tool Artifact (`file_path` = quel file, `icon: "pen"`, `capabilities: {"assets": {}, "db": {}}`).
   Per aggiornare l'immagine ripubblica lo stesso file (stesso link).
4. Quando l'utente scrive "fatto": `ArtifactData` query su collection `segni` ordinata per `quando` desc, limit 1;
   scarica l'immagine con Artifact `read` + `path` = asset_id e guardala.
5. Interpreta il tratto rispetto alla scala dell'immagine (misura pixel → mm usando un elemento noto, es. il
   diametro dell'asse 6 mm) e ripeti il disegno a parole all'utente prima di modificare il modello.

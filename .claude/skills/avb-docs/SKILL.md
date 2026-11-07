---
name: avb-docs
description: Aggiornare la documentazione dell'AvocadoBook (scheda di stampa e istruzioni di montaggio IT/EN in PDF, descrizioni per i siti in 12 lingue, anteprime, pacchetto di caricamento).
---
# Documentazione

- Sorgenti in `docs/src/*.html` (IT + EN, stessa struttura: modifica sempre ENTRAMBE le lingue) → PDF con
  `NODE_PATH=$(npm root -g) node tools/build_docs.js` → `docs/pdf/`. Controlla le pagine (`pdftoppm -r 40`) una volta.
- Immagini: `python3 tools/render.py all` → `build/img/` → copia in `docs/img/` quelle cambiate.
- Descrizioni: `descriptions/NN_LL_*.txt` (12 lingue, stessa struttura: TITLE/SUMMARY/DESCRIPTION…). Cambi una
  riga → cambiala in tutte le 12 lingue; frasi in prima persona neutre rispetto al genere (polacco, russo);
  stile con emoji. Poi `python3 tools/package.py` rigenera il file unico "00_TUTTE_LE_LINGUE" e lo zip.
- Limiti dei siti: descrizione profilo ≤1000 caratteri (conta con python). Niente dati personali (solo il nome dell'autore).
- Le traduzioni: `avb-docs-writer` (sonnet/low) basta; per testi lunghi in 12 lingue delega e verifica solo il numero di righe.

---
name: avb-slicer-project
description: Progetto multi-piatto per Anycubic Slicer Next (Kobra X + ACE), impostazioni di stampa, avvisi/errori dello slicer e caricamento del profilo di stampa su Maker Online o MakerWorld.
---
# Progetto per lo slicer e caricamento

- Il progetto lo scrive `src/progetto_unico.py` (struttura copiata da un file salvato dall'utente: oggetti centrati
  sull'origine, passo piatti 314,4 × 328,8 mm, impostazioni da `src/impostazioni_kobrax_utente.json` + `ST` e
  override per piatto `OVR` + modificatori `MODS` in `src/esporta_piatti.py`). Un oggetto per piatto, una parte per materiale.
- Cambiare un'impostazione: modifica `ST`/`OVR` in `esporta_piatti.py` (mai il 3MF a mano), riesporta,
  `tools/check_exports.py`, e aggiorna `docs/src/*print_sheet*`/`scheda_stampa*`.
- Avvisi noti: "troppo vicino agli altri" (oggetti separati) → già risolto; "temperature degli ugelli…" → valori
  `_HS/_BRASS` allineati, e sul piatto molle (PLA+PETG) resta informativo; G-code non accettato dai siti.
- **Maker Online** (Anycubic): tipo FDM; "Print Profile Files" = 3MF **salvato da Anycubic Slicer Next ≥1.4**
  (Apri → Taglia tutte → Salva progetto); il paragrafo rosso "Ensure your print profile…" è fisso, non un errore;
  i file rifiutati mostrano una ✖ e "View the failure reasons". Revisione 2–3 giorni. Etichetta IA obbligatoria,
  foto reali richieste. Descrizione profilo ≤1000 caratteri: testo in `descriptions/` (vedi skill avb-docs).
- **MakerWorld**: il profilo di stampa vuole un 3MF di Bambu Studio; con altre stampanti carica solo i file.
- Licenza scelta: CC BY-NC-SA 4.0 (uso commerciale su richiesta all'autore).

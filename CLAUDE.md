# AvocadoBook – laptop giocattolo stampabile (regole di lavoro per Claude)

Rispondi all'utente in **italiano**. Il modello è **parametrico**: si modifica solo `src/genera_laptop.py`
(+ `tasto_z.py`, `guide_alette.py`), mai gli STL/3MF a mano.

## Struttura
- `src/genera_laptop.py` → `build/parts.pkl` (tutti i pezzi già orientati per la stampa)
- `src/esporta_piatti.py` → `build/print/` (7 piatti 3MF, STL, progetto `AvocadoBook_progetto.3mf`)
- `src/coupon_*.py` → `build/tests/` (piccoli pezzi di prova da stampare prima del pezzo intero)
- `tools/verify.py` (verifiche geometriche), `tools/check_exports.py` (file esportati), `tools/render.py`
  (anteprime/sezioni), `tools/thickness_map.py`, `tools/build_docs.js` (PDF), `tools/package.py`, `tools/make_editor.py`
- `print/` = file pubblicati (copiati da `build/` solo dopo verifiche OK). `docs/src` HTML → `docs/pdf`.
- `descriptions/` testi per i siti (12 lingue), `TODO_v2.md` problemi aperti e idee.

## Pipeline standard (dopo ogni modifica geometrica)
```
python3 src/genera_laptop.py && python3 tools/verify.py --fast && python3 src/esporta_piatti.py && python3 tools/check_exports.py
```
Prima della consegna: `python3 tools/verify.py` completo (lento, ~10-20 min: lancialo in background).
Poi copia `build/print/*` in `print/`, rigenera coupon/anteprime/PDF se toccati, aggiorna `TODO_v2.md`.
Ogni modifica nel generatore: commento con tag versione (`# v27g: …`) che dice cosa e PERCHÉ (quale prova/foto).

## Instradamento (router): quale skill / agente, con quale modello e sforzo
Scegli il livello più economico che dà un risultato affidabile. La sessione principale orchestra e parla con
l'utente; delega i lavori meccanici e lunghi, tiene per sé (o all'agente CAD) le decisioni di progetto.

| Richiesta | Skill | Delega a (modello / effort) |
|---|---|---|
| Foto di un difetto di stampa o di montaggio, "non funziona", "si rompe" | `avb-print-doctor` | `avb-print-doctor` (sonnet / high) |
| Cambiare forma, tolleranze, meccanismi (tasti, cerniera, ganci, USB, scritte) | `avb-geometry-change` | `avb-cad-engineer` (opus / high) |
| Rigenerare + verificare + esportare dopo una modifica | `avb-verify` | `avb-verifier` (haiku / low) |
| Pezzo di prova di una zona | `avb-coupon` | sessione principale (pochi comandi) |
| Avvisi/errori dello slicer, progetto multi-piatto, upload su Maker Online/MakerWorld | `avb-slicer-project` | sessione principale; rigenerazione → `avb-verifier` |
| Schede di stampa, istruzioni, descrizioni, traduzioni, pacchetto | `avb-docs` | `avb-docs-writer` (sonnet / low) |
| L'utente deve indicare un punto su un'immagine | `avb-sketch-feedback` | sessione principale |
Regole di costo: non delegare compiti da 1-3 comandi; un solo agente alla volta salvo lavori indipendenti;
passa all'agente percorsi e obiettivo, non incollare file; chiedi risultati sintetici (OK/FAIL + numeri).

## Regole apprese (non violarle)
### File di stampa
- Progetto per Anycubic Slicer Next/ACnext: **un oggetto per piatto, una parte per materiale** ("1 GRIGIO PETG – …").
  Oggetti separati per colore che si toccano → avviso "troppo vicino" e Maker Online rifiuta il file.
- Il file da caricare sui siti è quello **salvato dallo slicer** (Apri → Taglia tutte → Salva progetto): ha anteprime e dati di verifica.
- Temperature uguali per tutti i tipi di ugello (`nozzle_temperature`, `_BRASS`, `_HS`, primo strato): PETG 230, PLA 225.
- Slot ACE: 1 PETG grigio, 2 PETG bianco, 3 PETG nero, 4 PLA (solo supporti). Piatti multicolore: angolo
  X 0–85 / Y 182–260 libero per la torre di spurgo.
- Modificatori `MOD_cerniera_piena_*` (100 %, 6 pareti) nel piatto 2: il 3MF separato del piatto non li ha.
### Stampa (PETG su PEI ruvido, Kobra X)
- Niente brim (si toglie solo con le forbici): orecchie a strappo sui pezzi grandi; piatto 80 °C; ventola 10–30 %; stampante coperta.
- Niente stiratura con il PETG (trascina grumi). Superficie superiore monotonica lenta.
- Sporgenze: prima scelta forme autoportanti a 45°. Supporti PLA che alternano strati PLA/PETG NON funzionano.
- Parti sottili (molle): stampate su un foglio di PLA da 0,4 mm, si staccano a mano.
- Distanza PETG–PETG ≥ 0,6 mm (0,2 si fonde). Gioco guide tasti 0,15. Fori piccoli escono ~0,4 mm più stretti.
- Incastri "a presa" (USB‑C): linguette elastiche (0,8 mm, fessura 0,6, dentino 0,3), non fori stretti.
- Archi sopra un asse si abbassano di 0,2–0,4 mm in stampa: prevedere gioco extra in alto.
### Verifiche obbligatorie
- Pezzi ESPORTATI chiusi e in un corpo; percorso di montaggio (ogni pezzo scende dall'alto senza urti);
  il piano scende sull'asse del coperchio aperto ≥105°; pelle superiore del piano ≥ 0,6 mm ovunque (tasche dei ganci!);
  rotazione coperchio 0–185° senza contatti; prima di stampare un pezzo grande, coupon della zona modificata.
- Non dichiarare "fatto" senza i numeri delle verifiche. Se un controllo fallisce, dillo.

## Stato (v1, pubblicata)
Tasti, molle, trackpad, USB‑C provati e OK. Problemi aperti in `TODO_v2.md` (coperchio che non chiude del tutto,
gioco sopra l'asse, posizioni intermedie dello schermo, finestrella cerniera, logo).
Nessun dato personale nel repository (solo il nome dell'autore).

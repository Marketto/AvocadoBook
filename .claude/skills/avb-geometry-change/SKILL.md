---
name: avb-geometry-change
description: Modificare la geometria dell'AvocadoBook (forme, tolleranze, tasti, molle, cerniera, ganci, porta USB-C, scritte, rampe) nel generatore parametrico, verificarla e preparare un coupon di prova. Usala per ogni richiesta che cambia un pezzo stampato.
---
# Modifica geometrica

1. **Capire il problema**: se viene da una foto, prima `avb-print-doctor`. Individua nel generatore il blocco
   (cerca i tag `# vNN` e le costanti in testa: KEY_*, TAB_*, HOOK_*, AX_*, HOOD_*, ZS_*, TP_*, USB*, WELL_*).
2. **Progettare con i vincoli** (CLAUDE.md, "Regole apprese"): 45° autoportante, ≥0,6 mm tra pezzi PETG,
   pelle ≥0,6 mm sopra cavità, gioco extra sopra gli archi, niente materiale che blocchi il montaggio dall'alto.
   Per forme decise dall'utente, mostra 2–3 proposte con `tools/render.py section` o un'immagine 2D prima di applicarle;
   se l'utente deve indicare un punto usa `avb-sketch-feedback`.
3. **Modificare** `src/genera_laptop.py` con un commento `# vNNx: cosa e perché`. Per profili usa `_yz_prism`,
   `CrossSection` + `offset` (raccordi), intersezioni con `box`.
4. **Verificare**: `python3 src/genera_laptop.py && python3 tools/verify.py --fast` (tutto OK), poi le verifiche mirate
   (es. sezione con `tools/render.py section`, spessori con `tools/thickness_map.py`). Se cambi la superficie del piano
   o del fondo, `tools/verify.py` completo (pelle superiore) in background.
5. **Esportare**: `python3 src/esporta_piatti.py && python3 tools/check_exports.py`.
6. **Coupon** della zona (skill `avb-coupon`) e anteprima da mostrare all'utente.
7. **Consegna**: copia `build/print/*` in `print/` solo se le verifiche sono OK; aggiorna `docs/src` se cambia
   stampa/montaggio; riassumi all'utente cosa è cambiato, i numeri delle verifiche e cosa ristampare.
Modello: le scelte di progetto richiedono precisione → agente `avb-cad-engineer` (opus/high) per modifiche
non banali; ritocchi di una costante li fa la sessione principale.

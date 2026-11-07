---
name: avb-coupon
description: Creare un piccolo pezzo di prova (coupon) di una zona del laptop da stampare in pochi minuti prima del pezzo intero (cerniera, porta USB-C, scritta sotto il fondo, tasto, trackpad...).
---
# Coupon di prova

Modello: copia uno di `src/coupon_*.py` (usbc, cerniera, scritta_fondo). Schema:
1. Esegui il generatore nel namespace (`__file__ = genera_laptop.py; exec(... split('# ================= checks')[0], globals())`).
2. Ritaglia: `pezzo = clean(<solido> ^ box(x0, x1, y0, y1, z0, z1))`; deve essere **un corpo** (`assert len(decompose()) == 1`).
3. Più materiali (es. scritta nera): esporta ogni parte con il nome che `gruppi_3mf.material()` riconosce
   (`…scritta_nera` = nero, `…lettere/logo/molle` = bianco, `PLA` = PLA).
4. Posiziona nella parte anteriore del piatto (angolo in alto a sinistra libero per la torre) e scrivi con
   `gruppi_3mf.write` (raggruppa per materiale) o con `progetto_unico.write` se servono impostazioni
   (es. riempimento 100 %: `{name: {"sparse_infill_density": "100%", "wall_loops": "6"}}`).
5. Nome `TEST_NN_descrizione`, in `build/tests/`; se approvato copialo in `print/tests/`.
Di' all'utente cosa controllare sul pezzo (incastro, rottura allo stacco, leggibilità…) e quanto dura la stampa.

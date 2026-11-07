---
name: avb-verify
description: Rigenerare e verificare l'AvocadoBook (geometria, rotazione coperchio, montaggio, pelle superiore, file esportati e progetto per lo slicer). Usala dopo ogni modifica e prima di consegnare file da stampare.
---
# Verifica

Comandi (dalla radice del repo):
```
python3 src/genera_laptop.py            # ~ secondi → build/parts.pkl
python3 tools/verify.py --fast          # 1-3 min: pezzi, tasti, trackpad, coperchio (ogni 5°), asse, discesa piano
python3 tools/verify.py                 # completo 10-20 min (in background): ogni 1°, inserimento molle/tasti, pelle ≥0,6
python3 src/esporta_piatti.py           # → build/print
python3 tools/check_exports.py          # STL chiusi, 1 oggetto per piatto, 2 modificatori, temperature allineate
```
Interpretazione:
- `fondo/piano ~7,3 mm3` è voluto (dentini dei ganci a scatto). Qualsiasi altro FAIL blocca la consegna.
- "piano scende sull'asse" FAIL → materiale del copri-asse sotto il centro dell'asse o davanti al foro.
- "pelle superiore" FAIL → una rampa/incisione buca le tasche dei ganci posteriori o i fori dei pioli.
- Rotazione FAIL a pochi gradi → copri-asse troppo avanti/alto vicino al bordo della tacca del coperchio.
Riporta sempre all'utente i numeri (OK/FAIL), non solo "tutto bene". Delegabile all'agente `avb-verifier`.

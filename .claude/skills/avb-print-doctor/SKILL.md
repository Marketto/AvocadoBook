---
name: avb-print-doctor
description: Diagnosticare problemi di stampa o di montaggio dell'AvocadoBook da foto o descrizioni (imbarcamento, fessure, pezzi rotti, incastri laschi o duri, tasti che si bloccano, coperchio che non chiude, superfici ruvide, avvisi dello slicer) e proporre la correzione più economica.
---
# Dottore di stampa

Procedura: 1) descrivi cosa vedi nella foto e localizza il pezzo/zona nel modello; 2) confronta con la casistica;
3) proponi prima rimedi senza ristampa (impostazioni, limetta, montaggio), poi una modifica + coupon;
4) se servono informazioni, chiedi UNA prova mirata e veloce (es. "monta senza il piano: chiude?").

Casistica già risolta (causa → rimedio):
- Brim da tagliare con le forbici → niente brim, orecchie a strappo (`orecchie.py`).
- Coperchio/piano imbarcati → piatto 80 °C, ventola 10–30 % e spenta nei primi 5 strati, stampante coperta, orecchie.
- Superficie superiore ruvida a grumi → stiratura OFF con PETG; superficie monotonica 40 mm/s, 8 strati superiori.
- Fessure sul piano dietro i numeri → rampa sopra le tasche dei ganci/pioli: pelle ≥0,6 mm (verify).
- Punta sottile che si stacca (copri-asse) → niente lamelle <1,7 mm stampate nel vuoto; 45°; modificatore 100 %; staccare a piatto freddo flettendo la lamiera.
- Pezzo che "balla" vicino alla cerniera → arco sopra l'asse abbassato in stampa: più gioco in alto (0,45).
- Coperchio che non chiude e fa resistenza → prove A (senza piano), B (premere il davanti), C (coperchio sul tavolo): scatti/incavi, imbarcamento o copri-asse.
- Schermo che sta su solo a ~105° → incavi del rullo solo a 0/105 (v2: 90/120/135).
- Molle che non entrano → nervature sopra le scanalature: percorso di montaggio (verify, inserimento).
- Tasto che si incastra / troppo gioco → alette sui 4 lati con canali, gioco 0,15, molle a S verticali "dura" 0,95.
- Porta USB-C lasca → linguette elastiche con dentino (test 20).
- Supporto PLA/PETG che si sfoglia → niente strati alternati; forme a 45° (trackpad, test 19).
- Avviso slicer "troppo vicino agli altri" → un oggetto per piatto; "temperature ugelli" → allineare `_HS/_BRASS`; con PLA+PETG sullo stesso piatto (molle) l'avviso è informativo.
Delegabile all'agente `avb-print-doctor` (vision + ragionamento).

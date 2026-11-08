"""Version 337 preview (Nawaz: "make a preview with all the client territories as well"). Runs on the current V5:
 1. tools/v333_v5_bosporan_kuban.py: the Bosporan client kingdom's Kuban (Krasnodar, Dinskoy, Seversky, Abinsky, Gelendzhik) and the land
    to his Version 333 red line from the Don corner;
 2. tools/v325_v5_exceptions.py: + the Tuapse coast (the Zilchi/Zichians, whose king received his kingdom from Hadrian, Arrian Periplus;
    Procopius Wars 8.4);
 3. tools/v332_v5_bohemia.py: + Bohemia, all of Czechia (the Marcomanni, whose kings ruled 'by Roman authority', Tacitus Germania 42;
    Roman troops in their land in the 170s, Dio 72.20).
Every other client kingdom (Armenia, Iberia, Lazica, Abasgi, Apsilae, Sanigae, Caucasian Albania, Osroene, Adiabene, Commagene, Emesa,
Nabataea, Judaea, Mauretania, Thrace, the Cottian Alps, the Quadi of Vannius, the Cherusci under Italicus, the Garamantes) is already in V5."""
import os, subprocess, sys
T = os.path.dirname(os.path.abspath(__file__))
for t in ['v333_v5_bosporan_kuban.py', 'v325_v5_exceptions.py', 'v332_v5_bohemia.py']:
    print('==', t); subprocess.check_call([sys.executable, os.path.join(T, t)])

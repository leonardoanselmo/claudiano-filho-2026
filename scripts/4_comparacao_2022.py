"""Compara os votos de 2026 com os de 2022, município a município.

Em 2022 Claudiano Filho foi eleito deputado estadual pelo PP com o mesmo número, 11555.
Baixa votacao_candidato_munzona_2022.zip (~640 MB, todos os estados) para brutos/ e
extrai só o arquivo de PE.

Entrada: dados/claudiano_filho_11555_por_municipio.csv (passo 1). Saída: dados/comparacao_2022.json
"""
import collections as C
import csv
import zipfile

from comum import BRUTOS, CANDIDATO, CDN, CSV_MUNICIPIOS, DADOS, baixar, salvar_json

NUMERO_2022, CARGO_2022 = CANDIDATO, '7'  # Deputado Estadual
csv22 = BRUTOS / 'votacao_candidato_munzona_2022_PE.csv'
if not csv22.exists():
    z = baixar(f'{CDN}/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip',
               BRUTOS / 'votacao_candidato_munzona_2022.zip')
    with zipfile.ZipFile(z) as zf:
        zf.extract(csv22.name, BRUTOS)

v22, situacao = C.Counter(), None
with open(csv22, encoding='latin-1') as f:
    for r in csv.DictReader(f, delimiter=';'):
        if r['NR_CANDIDATO'] == NUMERO_2022 and r['CD_CARGO'] == CARGO_2022:
            v22[r['NM_MUNICIPIO']] += int(r['QT_VOTOS_NOMINAIS'])  # soma as zonas
            situacao = (r['DS_SIT_TOT_TURNO'], r['SG_PARTIDO'])
print(f'2022: {sum(v22.values())} votos, {situacao}')

with open(DADOS / CSV_MUNICIPIOS, encoding='utf-8-sig') as f:
    v26 = {r[0]: int(r[1]) for r in list(csv.reader(f, delimiter=';'))[1:]}

comp = sorted(([m, v22.get(m, 0), v26.get(m, 0), v26.get(m, 0) - v22.get(m, 0)]
               for m in set(v22) | set(v26) if v22.get(m) or v26.get(m)), key=lambda x: (-(x[1] + x[2]), x[0]))
print(f'com voto em 2022: {sum(1 for c in comp if c[1])}, em 2026: {sum(1 for c in comp if c[2])}')
salvar_json(dict(tot22=sum(v22.values()), sit22=situacao, comp=comp), 'comparacao_2022.json')

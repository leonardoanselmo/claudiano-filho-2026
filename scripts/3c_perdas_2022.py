"""Correntes, 2022 × 2026: onde Claudiano Filho mais perdeu votos e Cayo Albino cresceu.

Os dois disputaram deputado estadual nas duas eleições: Claudiano com o 11555 e Cayo Albino com o 40400.
No resultado, as chaves "iz" são do candidato (Claudiano) e "ca" do rival (Cayo Albino).

Cada ano usa o próprio cadastro de locais (1º turno), ligado pela seção. As seções e alguns locais
mudaram entre as eleições (284 seções em 2022, 292 em 2026), então a comparação principal é por
bairro. A comparação por local só junta locais com o mesmo código nos dois anos; os demais são
somados em "locais que mudaram".

Baixa para brutos/ (~150 MB): votacao_secao_2022_PE.zip e eleitorado_local_votacao_2022.zip.
Usa também os downloads de 2026 do passo 3. Saída: dados/perda_2022x2026.json
"""
import collections as C
import csv
import io
import zipfile

from comum import BRUTOS, CANDIDATO, CARGO, CDN, PERDA as MUNICIPIO, RIVAL, baixar, salvar_json

CAND = {'2022': (CARGO, CANDIDATO), '2026': (CARGO, CANDIDATO)}   # candidato
RIV = {'2022': (CARGO, RIVAL), '2026': (CARGO, RIVAL)}         # rival
ARQ = {
    '2022': (('votacao_secao/votacao_secao_2022_PE.zip', 'votacao_secao_2022_PE.csv'),
             ('eleitorado_locais_votacao/eleitorado_local_votacao_2022.zip', 'eleitorado_local_votacao_2022.csv')),
    '2026': (('votacao_secao/votacao_secao_2026_PE.zip', 'votacao_secao_2026_PE.csv'),
             ('eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip', 'eleitorado_local_votacao_2026_PE.csv')),
}


def ler(caminho, membro):
    zp = baixar(f'{CDN}/{caminho}', BRUTOS / caminho.split('/')[-1])
    with zipfile.ZipFile(zp) as z, z.open(membro) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='latin-1'), delimiter=';'):
            if r['NM_MUNICIPIO'] == MUNICIPIO and r['NR_TURNO'] == '1':
                yield r


def ano(a):
    (vz, vm), (lz, lm) = ARQ[a]
    cadastro = {(r['NR_ZONA'], r['NR_SECAO']): r for r in ler(lz, lm)}
    loc = C.defaultdict(lambda: dict(iz=0, ca=0, val_iz=0, val_fed=0, secoes=set(), nome='', bairro='', lat='', lon=''))
    for r in ler(vz, vm):
        cad = cadastro[(r['NR_ZONA'], r['NR_SECAO'])]
        x = loc[cad['NR_LOCAL_VOTACAO']]
        x.update(nome=cad['NM_LOCAL_VOTACAO'], bairro=cad['NM_BAIRRO'], lat=cad.get('NR_LATITUDE', ''), lon=cad.get('NR_LONGITUDE', ''))
        x['secoes'].add(r['NR_SECAO'])
        cargo, num, votos = r['CD_CARGO'], r['NR_VOTAVEL'], int(r['QT_VOTOS'])
        valido = num not in ('95', '96')
        if (cargo, num) == CAND[a]:
            x['iz'] += votos
        if (cargo, num) == RIV[a]:
            x['ca'] += votos
        if valido and cargo == CAND[a][0]:
            x['val_iz'] += votos       # válidos do cargo que o candidato disputou naquele ano
        if valido and cargo == CARGO:
            x['val_fed'] += votos      # válidos do cargo do rival (o mesmo, deputado estadual)
    return loc


L = {a: ano(a) for a in ('2022', '2026')}
for a, loc in L.items():
    print(a, f"{len(loc)} locais, {sum(len(x['secoes']) for x in loc.values())} seções,",
          f"candidato {sum(x['iz'] for x in loc.values())}, rival {sum(x['ca'] for x in loc.values())}")


def pct(v, t):
    return round(100 * v / t, 2) if t else 0.0


# por bairro
bairros = C.defaultdict(lambda: {a: dict(iz=0, ca=0, val_iz=0, val_fed=0) for a in L})
for a, loc in L.items():
    for x in loc.values():
        for k in ('iz', 'ca', 'val_iz', 'val_fed'):
            bairros[x['bairro']][a][k] += x[k]
saida_bairros = sorted(([b, v['2022']['iz'], v['2026']['iz'], pct(v['2022']['iz'], v['2022']['val_iz']), pct(v['2026']['iz'], v['2026']['val_iz']),
                         v['2022']['ca'], v['2026']['ca'], pct(v['2022']['ca'], v['2022']['val_fed']), pct(v['2026']['ca'], v['2026']['val_fed'])]
                        for b, v in bairros.items()), key=lambda r: r[2] - r[1])

# por local com o mesmo código nos dois anos
comuns = set(L['2022']) & set(L['2026'])
saida_locais = []
for k in comuns:
    x22, x26 = L['2022'][k], L['2026'][k]
    saida_locais.append([x26['nome'], x26['bairro'], x22['iz'], x26['iz'], x22['ca'], x26['ca'],
                         len(x22['secoes']), len(x26['secoes']), x22['nome'] if x22['nome'] != x26['nome'] else '',
                         pct(x22['iz'], x22['val_iz']), pct(x26['iz'], x26['val_iz']), pct(x22['ca'], x22['val_fed']), pct(x26['ca'], x26['val_fed']),
                         x26['lat'], x26['lon']])
saida_locais.sort(key=lambda r: r[3] - r[2])
mudaram = {a: [L[a][k]['nome'] for k in set(L[a]) - comuns] for a in L}
resto = {a: [sum(L[a][k]['iz'] for k in set(L[a]) - comuns), sum(L[a][k]['ca'] for k in set(L[a]) - comuns)] for a in L}

tot = {a: dict(iz=sum(x['iz'] for x in L[a].values()), ca=sum(x['ca'] for x in L[a].values()),
               val_iz=sum(x['val_iz'] for x in L[a].values()), val_fed=sum(x['val_fed'] for x in L[a].values())) for a in L}
# associação entre a queda do candidato e a alta do rival, por local comum, em pontos percentuais
# (em votos absolutos a correlação seria inflada pelo tamanho do local)
dx = [r[10] - r[9] for r in saida_locais]
dy = [r[12] - r[11] for r in saida_locais]
mx, my = sum(dx) / len(dx), sum(dy) / len(dy)
cor = sum((a - mx) * (b - my) for a, b in zip(dx, dy)) / (sum((a - mx) ** 2 for a in dx) * sum((b - my) ** 2 for b in dy)) ** 0.5
print(f'{len(comuns)} locais comuns; correlação entre as variações em pontos percentuais: {cor:.2f}')
salvar_json(dict(tot=tot, bairros=saida_bairros, locais=saida_locais, mudaram=mudaram, resto=resto, cor=round(cor, 2)),
            'perda_2022x2026.json')

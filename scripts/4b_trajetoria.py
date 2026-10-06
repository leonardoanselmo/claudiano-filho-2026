"""Trajetória de Claudiano Filho para deputado estadual, de 2010 a 2026.

Ele mudou de número e de partido (PSDB 45645, depois PP 11555), então as candidaturas antigas são
achadas pelo nome completo. Em 2002 e 2006 não há candidatura com esse nome; quem disputou foi
Claudiano Ferreira Martins (sem "Filho"), PMDB 15215, eleito nas duas, com a mesma base eleitoral.
Esses dois resultados entram só como nota de contexto (chave "antes"), não na trajetória.

Para cada eleição de 2002 a 2018, lê só o arquivo
de Pernambuco de dentro do zip nacional do TSE (votacao_candidato_munzona_AAAA.zip), por leitura parcial
via HTTP, sem baixar o arquivo inteiro; o resultado fica em brutos/hist/. 2022 vem do passo 4 e 2026 do
passo 1.

Os nomes dos municípios mudam de grafia entre os arquivos (com e sem acento); a junção usa o nome sem
acento e exibe a grafia de 2026.

Saída: dados/trajetoria.json
"""
import collections as C
import csv
import unicodedata

from comum import BRUTOS, CDN, NOME_COMPLETO, ler_json, salvar_json
from remotezip import extrair

ANOS = [2010, 2014, 2018, 2022]
ANTES = [2002, 2006]
NOME_ANTES = 'CLAUDIANO FERREIRA MARTINS'


def sem_acento(s):
    s = ''.join(ch for ch in unicodedata.normalize('NFKD', s.upper()) if not unicodedata.combining(ch))
    return {'JABOATAO': 'JABOATAO DOS GUARARAPES', 'CABO': 'CABO DE SANTO AGOSTINHO', 'ITAMARACA': 'ILHA DE ITAMARACA',
            'SAO CAETANO': 'SAO CAITANO'}.get(s, s)


def arquivo(ano):
    if ano == 2022:
        return BRUTOS / 'votacao_candidato_munzona_2022_PE.csv'
    destino = BRUTOS / 'hist' / f'munzona_{ano}_PE.csv'
    if not destino.exists():
        destino.parent.mkdir(exist_ok=True)
        print(f'lendo o trecho de PE do arquivo de {ano}')
        extrair(f'{CDN}/votacao_candidato_munzona/votacao_candidato_munzona_{ano}.zip',
                lambda n: n.upper().endswith('_PE.CSV'), destino)
    return destino


nomes26 = {sem_acento(m['nome']): m['nome'] for m in ler_json('municipios.json')}
eleicoes, por_cidade = [], C.defaultdict(dict)
for ano in ANOS:
    tot, info = C.Counter(), None
    with open(arquivo(ano), encoding='latin-1') as f:
        for r in csv.DictReader(f, delimiter=';'):
            if r['NM_CANDIDATO'] == NOME_COMPLETO and r['CD_CARGO'] == '7' and r.get('NR_TURNO', '1') == '1':
                tot[sem_acento(r['NM_MUNICIPIO'])] += int(r['QT_VOTOS_NOMINAIS'] or 0)
                info = dict(ano=ano, numero=r['NR_CANDIDATO'], partido=r['SG_PARTIDO'], situacao=r['DS_SIT_TOT_TURNO'])
    if not info:
        print(ano, 'sem candidatura')
        continue
    info.update(votos=sum(tot.values()), municipios=sum(1 for v in tot.values() if v))
    eleicoes.append(info)
    for m, v in tot.items():
        por_cidade[m][ano] = v
    print(ano, info)

oficial = ler_json('resultado_oficial.json')
estado = ler_json('resultado_estado.json')
mun26 = ler_json('municipios.json')
eleicoes.append(dict(ano=2026, numero=oficial['ela']['n'], partido=oficial['ela']['sg'], situacao=oficial['ela']['st'].upper(),
                     votos=oficial['ela']['v'], municipios=sum(1 for m in mun26 if m['votos'])))
for m in mun26:
    if m['votos']:
        por_cidade[sem_acento(m['nome'])][2026] = m['votos']

antes = []
for ano in ANTES:
    tot, info = C.Counter(), None
    with open(arquivo(ano), encoding='latin-1') as f:
        for r in csv.DictReader(f, delimiter=';'):
            if r['NM_CANDIDATO'] == NOME_ANTES and r['CD_CARGO'] == '7' and r.get('NR_TURNO', '1') == '1':
                tot[sem_acento(r['NM_MUNICIPIO'])] += int(r['QT_VOTOS_NOMINAIS'] or 0)
                info = dict(ano=ano, nome=r['NM_URNA_CANDIDATO'], numero=r['NR_CANDIDATO'], partido=r['SG_PARTIDO'], situacao=r['DS_SIT_TOT_TURNO'])
    if info:
        info.update(votos=sum(tot.values()), top=[nomes26.get(m, m) for m, _ in tot.most_common(3)])
        antes.append(info)
print('antes (outro candidato):', antes)
anos = [e['ano'] for e in eleicoes]
ranking = sorted(por_cidade.items(), key=lambda kv: -sum(kv[1].values()))[:15]
cidades = [[nomes26.get(m, m), [v.get(a, 0) for a in anos]] for m, v in ranking]
print('maiores cidades na soma:', [c[0] for c in cidades[:6]])
salvar_json(dict(anos=anos, eleicoes=eleicoes, cidades=cidades, antes=antes), 'trajetoria.json')

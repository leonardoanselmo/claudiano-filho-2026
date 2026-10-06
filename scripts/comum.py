"""Caminhos, parâmetros da candidata e funções compartilhadas pelos scripts."""
import json
import os
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / 'dados'      # resultados pequenos, versionados
BRUTOS = RAIZ / 'brutos'    # downloads grandes do TSE, fora do Git
DADOS.mkdir(exist_ok=True)
BRUTOS.mkdir(exist_ok=True)

CANDIDATO = '11555'         # Claudiano Filho (PP, Federação União Progressista)
NOME_COMPLETO = 'CLAUDIANO FERREIRA MARTINS FILHO'  # para achar as candidaturas antigas, com outros números
CARGO = '7'                 # Deputado Estadual
CARGO_ARQ = '0007'
BASE = 'CAETÉS'             # município onde ele teve mais votos em 2026
PERDA = 'CORRENTES'         # município onde ele mais perdeu votos de 2022 para 2026
RIVAL = '40400'             # Cayo Albino (PSB), que ganhou Correntes
UF = 'pe'
API = 'https://resultados.tse.jus.br/oficial/ele2026'
ELEICAO = '6259'            # Eleição Ordinária Estadual 2026, 1º turno
CDN = 'https://cdn.tse.jus.br/estatistica/sead/odsele'
CSV_MUNICIPIOS = 'claudiano_filho_11555_por_municipio.csv'
CSV_SECOES = 'claudiano_filho_11555_por_secao.csv'


def get_json(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read().decode('utf-8'))


def baixar(url, destino):
    """Baixa um arquivo grande só se ele ainda não existir em brutos/."""
    destino = Path(destino)
    if destino.exists():
        print(f'já existe: {destino.name}')
        return destino
    print(f'baixando {url}')
    tmp = destino.with_suffix(destino.suffix + '.part')
    urllib.request.urlretrieve(url, tmp)
    os.replace(tmp, destino)
    return destino


def salvar_json(obj, nome):
    with open(DADOS / nome, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))


def ler_json(nome):
    with open(DADOS / nome, encoding='utf-8') as f:
        return json.load(f)


def municipios_pe():
    """Lista de municípios de PE com código TSE (cd) e IBGE (cdi)."""
    mun = get_json(f'{API}/{ELEICAO}/config/mun-e00{ELEICAO}-cm.json')
    return [x for x in mun['abr'] if x['cd'] == UF][0]['mu']


def candidatos(d):
    """Todos os candidatos do cargo num arquivo de resultado: (candidato, partido, agremiação)."""
    for cargo in d['carg']:
        if cargo['cd'] != CARGO:
            continue
        for a in cargo['agr']:
            for p in a['par']:
                for k in p.get('cand', []):
                    yield k, p, a

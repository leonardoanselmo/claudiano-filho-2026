"""Resultado oficial de deputado estadual em PE: vagas por partido/federação e a lista da federação do candidato.

Usa a proclamação do TSE (campos de eleito, situação e vagas do arquivo de resultado). Se o TSE
ainda não tiver proclamado, o script avisa e para.

Entrada: dados/resultado_estado.json (passo 1). Saída: dados/resultado_oficial.json
"""
from comum import CANDIDATO, candidatos, ler_json, salvar_json

estado = ler_json('resultado_estado.json')
cargo = next(c for c in estado['carg'])
eleitos = [(int(k['vap']), k, p) for k, p, _ in candidatos(estado) if k['e'] == 's']
if len(eleitos) < int(cargo['nv']):
    raise SystemExit(f"O TSE ainda não proclamou todos os eleitos ({len(eleitos)} de {cargo['nv']}).")

vagas = []
for a in cargo['agr']:
    if int(a['vag']) == 0:
        continue
    votos = sum(int(p.get('tvtn', 0)) + int(p.get('tvtl', 0)) for p in a['par'])
    vagas.append(dict(nm=a['com'], v=votos, s=int(a['vag'])))
vagas.sort(key=lambda x: -x['v'])

agrem = next(a for k, p, a in candidatos(estado) if k['n'] == CANDIDATO)
lista = []
for k, p, a in candidatos(estado):
    if a['n'] == agrem['n']:
        lista.append(dict(n=k['n'], nm=k['nmu'], sg=p['sg'], v=int(k['vap']), e=k['e'] == 's', st=k['st']))
lista.sort(key=lambda x: -x['v'])
ela = next(x for x in lista if x['n'] == CANDIDATO)
ultimo = min((x for x in lista if x['e']), key=lambda x: x['v'])
menor = min(eleitos, key=lambda x: x[0])
print(f"{len(eleitos)} eleitos, {len(vagas)} agremiações com vaga")
print(f"Candidato(a): {ela['v']} votos, {ela['st']}; último eleito do partido: {ultimo['nm']} com {ultimo['v']}"
      f" (faltaram {ultimo['v'] - ela['v'] + 1})")
salvar_json(dict(agremiacao=agrem['nm'], sigla=agrem['com'], vagas_agrem=int(agrem['vag']), qe=int(cargo['qe']), nv=int(cargo['nv']), vagas=vagas, lista=lista[:12], ela=ela, ultimo=ultimo,
                 faltaram=ultimo['v'] - ela['v'] + 1, menor_eleito=[menor[0], menor[1]['nmu'], menor[2]['sg']]),
            'resultado_oficial.json')

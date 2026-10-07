# Claudiano Filho 11555 em 2026

Para onde foram os votos de Claudiano Filho (Claudiano Ferreira Martins Filho, PP, Federação União Progressista, número 11555) para deputado estadual em Pernambuco, no 1º turno de 04/10/2026.

**Site:** https://leonardoanselmo.github.io/claudiano-filho-2026/
**PDF:** [relatorio/Claudiano_Filho_11555_2026.pdf](relatorio/Claudiano_Filho_11555_2026.pdf)

Eleito deputado estadual em 2010 e 2014 (PSDB, 45645) e em 2018 e 2022 (PP, 11555), ele teve 44.565 votos em 2026 e ficou como **1º suplente da Federação União Progressista**, a 1.988 votos da última eleita.

O relatório tem:
- mapa de Pernambuco com os votos por município;
- os 162 municípios onde ele teve voto, com a posição dele em cada um;
- trajetória de 2010 a 2026, com as cidades que mais votaram nele em cada eleição;
- 2022 × 2026 por município: onde perdeu e onde ganhou votos;
- Caetés, a cidade que mais votou nele em 2026, por bairro e por local de votação;
- Correntes 2022 × 2026, onde ele mais perdeu: Claudiano e Cayo Albino lado a lado, com mapa dos locais de votação;
- votos em cada seção eleitoral de PE, sem misturar as seções agregadas;
- resultado oficial: a lista da federação e quantos votos faltaram para a vaga.

## Estrutura

| Pasta / arquivo | Conteúdo |
|---|---|
| `index.html` | O site publicado no GitHub Pages (gerado pelo passo 6) |
| `scripts/` | Coleta e análise, numeradas na ordem em que rodam |
| `scripts/comum.py` | Parâmetros do candidato (número, cargo, cidade-base, cidade da maior perda, rival) e funções compartilhadas |
| `scripts/template.html` | Modelo da página. Os dados são inseridos no passo 6 |
| `dados/` | Resultados pequenos que alimentam o site e o PDF |
| `relatorio/` | Versão em PDF (gerada pelo passo 7) |
| `brutos/` | Downloads grandes do TSE (fora do Git, criados pelos scripts) |

## Como atualizar

Requer Python 3.10 ou mais novo. Os passos 1 a 6 usam só a biblioteca padrão.

```bash
cd scripts
python 1_coleta_municipios.py   # API do TSE: votos, % e posição do 11555 nos 185 municípios
python 2_resultado_oficial.py   # vagas por partido e lista da federação (resultado proclamado)
python 3_base_secoes.py         # Caetés por local de votação e bairro (~280 MB na 1ª vez)
python 3b_votos_por_secao.py    # votos do 11555 em cada seção de PE (mesmos downloads do passo 3)
python 3c_perdas_2022.py        # Correntes 2022 x 2026, Claudiano e Cayo Albino (~150 MB de 2022)
python 4_comparacao_2022.py     # 2022 x 2026 por município (~640 MB na 1ª vez)
python 4b_trajetoria.py         # trajetória 2010-2026 (lê só o trecho de PE dos arquivos antigos)
python 5_mapa.py                # contornos dos municípios e votos por código IBGE
python 6_monta_site.py          # gera dados/relatorio.json e index.html
```

Para gerar o PDF:

```bash
pip install -r requirements.txt
python scripts/7_gera_pdf.py
```

Os arquivos grandes ficam em `brutos/` e só são baixados se ainda não existirem. Para as eleições de 2002 a 2018, o passo 4b lê só o arquivo de Pernambuco de dentro do zip nacional do TSE (leitura parcial por HTTP, em `scripts/remotezip.py`).

## Trajetória e o nome do candidato

Claudiano Filho mudou de número e de partido ao longo do tempo, então as candidaturas antigas são achadas pelo nome completo (`CLAUDIANO FERREIRA MARTINS FILHO`). Em 2002 e 2006 não há candidatura com esse nome: quem disputou foi Claudiano Ferreira Martins, sem o "Filho" (PMDB, 15215), eleito nas duas, com a mesma base eleitoral. Os dados do TSE não informam a relação entre os dois, então esses anos aparecem só como nota, fora da trajetória.

## Seções agregadas e consolidadas

Quando uma seção é agregada a outra, os eleitores dela votam na urna da seção principal, e o TSE publica o resultado só na principal. O arquivo de votos por seção não tem linhas para as agregadas: em PE são 673 agregadas, somadas em 626 seções principais.

Por isso, o passo 3b:
- não cria linha para seção agregada (e confere que nenhuma agregada tem voto próprio);
- marca a principal como consolidada e lista as agregadas que ela recebe;
- soma o eleitorado da principal com o das agregadas, para o percentual não misturar bases.

O arquivo de locais de votação repete cada seção para o 1º e o 2º turno. Os scripts usam só as linhas do 1º turno e ligam cada seção ao local pela própria seção.

## Fontes

- [API de resultados do TSE](https://resultados.tse.jus.br/oficial/ele2026/6259/dados/pe/pe-c0007-e006259-u.json): votos por município e resultado oficial (eleição 6259, cargo 7).
- [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/): `votacao_candidato_munzona` de 2002 a 2022, `votacao_secao_2022_PE`, `votacao_secao_2026_PE`, `eleitorado_local_votacao_2022` e `eleitorado_local_votacao_2026`.
- Contornos dos municípios: [geodata-br](https://github.com/tbrugz/geodata-br), a partir da malha do IBGE.

## Sobre o PDF

As dicas ao passar o mouse no PDF aparecem no Adobe Acrobat Reader e no Firefox. O leitor de PDF do Chrome e do Edge não as mostra. Para a versão interativa em qualquer navegador, use o site.

---

## Quem desenvolveu?

<img src="img/leo.jpg" alt="Foto de Léo Ansélmo" width="96" align="left">

**Léo Ansélmo** — Bacharelado em Administração e Desenvolvimento de Sistemas, com mais de 20 anos de experiência na área.

Procurei desenvolver um relatório baseado nos dados do TSE, mostrando o panorama político do candidato para o mesmo entender os dados consolidados e gerar conhecimento agregado da campanha atual.

Com ajuda da inteligência artificial (AI) nos mapas e gráficos, obtendo uma compreensão visual mais detalhada.

Instagram: [@leonardoanselmo79](https://www.instagram.com/leonardoanselmo79/)

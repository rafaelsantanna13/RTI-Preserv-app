# RTI + Preservação

Aplicativo Streamlit para comparação dimensional de flanges, estojos e porcas,
consulta da classificação RTI e orientação de preservação nas tabelas do projeto.

## Executar

```sh
python -m pip install -r requirements.txt
python -m streamlit run appvisu.py
```

`app.py` também abre a mesma interface. No Streamlit Community Cloud, mantenha
o arquivo de entrada já configurado; ambas as entradas são suportadas.

## Interface

1. Identifique a junta: norma/série, tipo de flange, NPS e classe.
   O diâmetro nominal do estojo é informado automaticamente em polegadas e mm.
2. Informe materiais, fluido, perda de massa e histórico.
3. Preencha as quatro medições em mm e pressione **Avaliar junta**.

O resultado mostra a aprovação dimensional, a classificação RTI, a preservação
e uma comparação individual entre cada medida e seu mínimo cadastrado.
Alterar qualquer entrada remove o resultado anterior até uma nova avaliação.
Os seletores de NPS e classe mostram somente combinações cadastradas.

## Organização

- `interface.py`: tela compartilhada, validação das entradas e apresentação.
- `avaliacao.py`: função de avaliação original, sem mudança dos critérios.
- `estojos.py`: consulta exata do estojo pela norma/série, NPS e classe;
  a avaliação também usa essa consulta, sem aceitar diâmetro nominal manual.
- `DiametrosEstojos.json`: correlação e fontes públicas dos fabricantes.
- `AvFlanges.json`, `AvEstojosPorcas.json`, `ClasseRTI.json`: tabelas originais.
- `.streamlit/config.toml`: cores do tema.

Esta revisão mantém os critérios de comparação e as tabelas originais de
limites e RTI. A escolha automática do estojo pode mudar o resultado em relação
a uma escolha manual incompatível com o flange. Não constitui uma revalidação
técnica dos limites de perda admissível cadastrados.

A correlação cobre as 181 combinações distintas (289 linhas de flange) do
cadastro atual: ASME B16.5 e ASME B16.47 Série A. Consulte
[fontes, cobertura e lacunas de critérios](docs/correlacao-estojos.md).

## Verificação

```sh
python -m unittest -v
```

Os testes verificam as duas entradas, campos vazios, igualdade ao limite,
reprovação individual, resultados obsoletos, ausência de classificação RTI e
combinações disponíveis nos seletores, valores de referência dos estojos,
seleção automática, mudanças dos limites, cobertura do cadastro e bloqueio
da avaliação quando faltam critérios para o diâmetro nominal identificado.

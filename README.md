# FlangeCheck

**Avaliação dimensional de juntas flangeadas.**

Compare as medidas de flange, estojo e porca com os mínimos cadastrados.
O resultado é exclusivamente dimensional: aprovado ou reprovado, com o
nominal, o mínimo e o medido de cada dimensão.

## Executar

```sh
python -m pip install -r requirements.txt
python -m streamlit run appvisu.py
```

`app.py` e `appvisu.py` abrem a mesma interface. O nome da interface e o título
do navegador são FlangeCheck; o repositório e o endereço de hospedagem atuais
são mantidos para preservar a publicação existente.

## Utilizar

1. Selecione norma/série, tipo, NPS e classe. O estojo nominal é automático.
2. Informe as quatro medições em mm e pressione **Avaliar junta**.

Os campos e os resultados mostram os valores **nominal**, **mínimo** e
**medido**. O nominal é uma referência; a aprovação usa `medido >= mínimo`
nas quatro dimensões. Alterar qualquer entrada invalida o resultado anterior.

Não há consulta ou sugestão de RTI/preservação nem campos para materiais,
fluido, histórico ou perda de massa. `ClasseRTI.json` permanece apenas como
arquivo histórico, sem importação, leitura ou uso durante a execução.

## Valores de referência

- Espessura nominal do flange: `tf_flange_mm` de `AvFlanges.json`.
- Diâmetro nominal do estojo: correlação por norma/série, NPS e classe,
  convertida de polegadas para mm.
- Altura e largura nominais da porca: `H_nom` e `F_nom` de `AvEstojosPorcas.json`.
- Os quatro mínimos são os originalmente cadastrados nessas tabelas.

A correlação cobre as 181 combinações distintas (289 linhas de flange) do
cadastro atual: B16.5 e B16.47 Série A. Confira
[fontes e lacunas de critérios](docs/correlacao-estojos.md).
A ausência dos limites para alguns estojos mantém a avaliação indisponível;
nenhum limite é extrapolado.

## Código e testes

- `interface.py`: tela compartilhada.
- `avaliacao.py`: referências e comparação dimensional, sem classificação adicional.
- `estojos.py` e `DiametrosEstojos.json`: seleção automática do nominal.

```sh
python -m unittest -v
```

Os testes cobrem correlação, valores nominais, aprovação pelo mínimo,
reprovação individual, entradas inválidas, atualização dos campos e remoção
das sugestões anteriores. Os critérios técnicos das tabelas não foram
revalidados nesta revisão.

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

1. Identifique a junta: tipo de flange, NPS, classe e diâmetro do estojo.
2. Informe materiais, fluido, perda de massa e histórico.
3. Preencha as quatro medições em mm e pressione **Avaliar junta**.

O resultado mostra a aprovação dimensional, a classificação RTI, a preservação
e uma comparação individual entre cada medida e seu mínimo cadastrado.
Alterar qualquer entrada remove o resultado anterior até uma nova avaliação.
Os seletores de NPS e classe mostram somente combinações cadastradas.

## Organização

- `interface.py`: tela compartilhada, validação das entradas e apresentação.
- `avaliacao.py`: função de avaliação original, sem mudança dos critérios.
- `AvFlanges.json`, `AvEstojosPorcas.json`, `ClasseRTI.json`: tabelas originais.
- `.streamlit/config.toml`: cores do tema.

Esta revisão mantém os dados e critérios do projeto; não constitui uma
revalidação técnica dos valores cadastrados.

## Verificação

```sh
python -m unittest -v test_interface.py
```

Os testes verificam as duas entradas, campos vazios, igualdade ao limite,
reprovação individual, resultados obsoletos, ausência de classificação RTI e
combinações disponíveis nos seletores.

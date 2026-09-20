# Correlação entre flange e diâmetro nominal do estojo

Consulta em 20/09/2026. Os dados de `DiametrosEstojos.json` são uma transcrição
dos diâmetros nominais dos quadros públicos dos fabricantes, com conferência
cruzada. Não são uma cópia licenciada das normas ASME; os quadros consultados
não identificam a edição da norma. Os limites de perda admissível do projeto não foram alterados nem revalidados.
Desde o FlangeCheck 3.0, as sugestões de RTI e preservação estão desativadas.

## Chave de consulta

**Norma + série (quando aplicável) + NPS + classe de pressão.**

As variantes de tipo cadastradas compartilham o mesmo diâmetro de estojo para
essa chave. O diâmetro nominal é distinto do diâmetro medido em campo e do
diâmetro de furo. Não há interpolação entre NPS, classes ou séries.

## Fontes

1. [Sigma Fasteners — Bolt Chart ASME B16.47 / B16.5](https://sigmafasteners.com/wp-content/uploads/2024/04/Bolt-Chart-ASME-B16.47-B16.5.pdf):
   página 1, B16.5 classes 150, 300, 600, 900, 1500 e 2500;
   página 2, B16.47 Série A classes 150, 300, 600 e 900.
   Foram transcritas as linhas **Stud Diameter**, conferindo os cabeçalhos
   no PDF renderizado. Nenhum comprimento de estojo foi importado.
2. [Texas Flange — Flange Bolt Chart](https://texasflange.com/products/flange-dims-weights/bolt-and-stud-dimensions-asme-b16-5-flanges/):
   conferência independente dos 112 pares NPS/classe B16.5 presentes no quadro Sigma.
3. Texas Flange — B16.5 [classe 150](https://texasflange.com/products/flange-dims-weights/ansi-b16-5-forged-flanges/class-150/),
   [classe 300](https://texasflange.com/products/flange-dims-weights/ansi-b16-5-forged-flanges/class-300/)
   e [classe 600](https://texasflange.com/products/flange-dims-weights/ansi-b16-5-forged-flanges/class-600/):
   complemento dos três pares de **NPS 22**, ausentes no quadro Sigma.
   A nota (a) especifica furo 1/8 pol maior que o estojo. Os furos correspondem
   a 1 3/8, 1 5/8 e 1 3/4 pol; portanto, os estojos são 1 1/4, 1 1/2 e 1 5/8 pol.
4. Texas Flange — B16.47 Série A:
   [150](https://texasflange.com/products/flange-dims-weights/ansi-b16-47-series-a-flanges/class-150-ser-a/),
   [300](https://texasflange.com/products/flange-dims-weights/ansi-b16-47-series-a-flanges/class-300-ser-a/),
   [600](https://texasflange.com/products/flange-dims-weights/ansi-b16-47-series-a-flanges/class-600-ser-a/),
   [900](https://texasflange.com/products/flange-dims-weights/ansi-b16-47-series-a-flanges/class-900-ser-a/).
   Os 66 pares foram conferidos pela coluna de furação e sua nota (2).

Resultado da conferência: 181 pares compatíveis com as fontes Texas Flange.
Na conferência dos catálogos que imprimem duas casas decimais, os valores
foram interpretados como suas frações de 1/8 pol (por exemplo, 1,38 representa
1 3/8). O arquivo final guarda frações nominais exatas; não usa os decimais
arredondados de furo para determinar o diâmetro durante a execução.

## Exemplos de referência

| Norma/série | NPS | Classe | Estojo nominal |
|---|---:|---:|---:|
| B16.5 | 8 | 150 | 3/4 pol |
| B16.5 | 8 | 300 | 7/8 pol |
| B16.5 | 8 | 600 | 1 1/8 pol |
| B16.5 | 3 | 900 | 7/8 pol |
| B16.47 A | 26 | 150 | 1 1/4 pol |
| B16.47 A | 26 | 300 | 1 5/8 pol |
| B16.47 A | 36 | 300 | 2 pol |
| B16.47 A | 38 | 300 | 1 1/2 pol |

A redução entre NPS 36 e 38 na Série A classe 300 é tabulada nas duas fontes;
não deve ser substituída por uma progressão crescente.

## Escopo e limites de avaliação ausentes

As 181 chaves cobrem todas as 289 linhas de `AvFlanges.json`, incluindo flanges
cegos, soldados e de virola. O cadastro atual não contém flanges B16.47 Série B
nem classe 400; a aplicação não oferece essas opções e não usa dados da Série A
para a Série B.

A correlação identifica alguns diâmetros que não existem em
`AvEstojosPorcas.json`. A interface mostra o nominal, informa a ausência dos
limites e interrompe a avaliação antes de aprovar/reprovar.
Não usa outro diâmetro nem extrapola limites de perda admissível.

| Norma/série | NPS | Classe | Estojo sem critérios cadastrados |
|---|---|---:|---:|
| B16.47 A | 32 | 900 | 3 1/4 pol |
| B16.47 A | 44 | 900 | 3 3/4 pol |
| B16.47 A | 46 e 48 | 900 | 4 pol |
| B16.47 A | 56 e 58 | 600 | 3 1/4 pol |

São seis chaves, presentes em 12 linhas (soldado/cego). Os critérios restantes
são os originais do projeto. Completar essas lacunas requer limites de estojo
e porca validados para os três diâmetros, além da correlação nominal.

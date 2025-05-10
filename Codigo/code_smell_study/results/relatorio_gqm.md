# Relat�rio GQM: Compara��o entre LLM e SonarQube na Detec��o de Code Smells

Reposit�rio analisado: **.repo**

## Quest�o 1: Qual das duas abordagens detecta mais code smells cl�ssicos?

### M�trica 1.1: N�mero total de code smells detectados

| Abordagem | Quantidade de Smells |
|-----------|----------------------|
| LLM | 7 |
| SonarQube | 12 |
| Diferen�a absoluta | 5 |
| Rela��o percentual (LLM/SonarQube) | 58.33% |

### M�trica 1.2: M�dia de code smells detectados por arquivo

| Abordagem | M�dia de Smells por Arquivo | Arquivos com Smells |
|-----------|------------------------------|---------------------|
| LLM | 7.00 | 1 |
| SonarQube | 6.00 | 2 |

### M�trica 1.3: Diferen�a m�dia de detec��o por arquivo

- Diferen�a m�dia por arquivo: **0.00**
- N�mero de arquivos comuns analisados: **0**

![Total de Code Smells](./q1_total_smells.png)

![M�dia por Arquivo](./q1_media_por_arquivo.png)

## Quest�o 2: As duas abordagens convergem ou divergem nos resultados?

### M�trica 2.1: Porcentagem de smells detectados simultaneamente

| M�trica | Valor |
|---------|-------|
| Smells detectados por ambas abordagens | 2 |
| Total de smells �nicos (uni�o) | 17 |
| Taxa de similaridade | 11.76% |

### M�trica 2.2: Porcentagem de smells exclusivos

| M�trica | Valor |
|---------|-------|
| Smells exclusivos LLM | 5 |
| Smells exclusivos SonarQube | 10 |
| Taxa de exclusividade LLM | 29.41% |
| Taxa de exclusividade SonarQube | 58.82% |

### M�trica 2.3: N�mero de categorias com alta/baixa sobreposi��o

| M�trica | Valor |
|---------|-------|
| Categorias com alta sobreposi��o (>80%) | 0 |
| Categorias com baixa sobreposi��o (<20%) | 5 |
| Total de categorias analisadas | 5 |

![Distribui��o de Smells](./q2_distribuicao_smells.png)

![Taxas Percentuais](./q2_taxas_percentuais.png)

![Sobreposi��o por Categoria](./q2_sobreposicao_por_categoria.png)

## Quest�o 3: Existem categorias de smells mais detectadas por cada abordagem?

### M�trica 3.1: N�mero m�dio de smells por categoria

- LLM: m�dia de **1.40** smells por categoria
- SonarQube: m�dia de **6.00** smells por categoria

| Categoria | LLM | SonarQube |
|-----------|-----|----------|
| Duplicate Code | 2 | 0 |
| Exception Handling | 1 | 6 |
| Feature Envy | 1 | 0 |
| Long Method | 2 | 0 |
| Magic Numbers | 1 | 6 |

### M�trica 3.2: Porcentagem de smells simult�neos por categoria

| Categoria | N�mero de Smells Simult�neos | % de Simultaneidade |
|-----------|------------------------------|--------------------|
| Duplicate Code | 0 | 0.00% |
| Exception Handling | 1 | 16.67% |
| Feature Envy | 0 | 0.00% |
| Long Method | 0 | 0.00% |
| Magic Numbers | 1 | 16.67% |

### M�trica 3.3: Porcentagem de smells exclusivos por categoria

| Categoria | Exclusivos LLM | % LLM | Exclusivos SonarQube | % SonarQube |
|-----------|----------------|-------|---------------------|-------------|
| Duplicate Code | 2 | 100.00% | 0 | 0.00% |
| Exception Handling | 0 | 0.00% | 5 | 83.33% |
| Feature Envy | 1 | 100.00% | 0 | 0.00% |
| Long Method | 2 | 100.00% | 0 | 0.00% |
| Magic Numbers | 0 | 0.00% | 5 | 83.33% |

![Contagem por Categoria](./q3_contagem_por_categoria.png)

![Percentual por Categoria](./q3_percentual_por_categoria.png)

![Heatmap de Categorias](./q3_heatmap_categorias.png)

## Conclus�es

### Quest�o 1: Qual das duas abordagens detecta mais code smells cl�ssicos?

O SonarQube detectou mais code smells (12) em compara��o com a abordagem LLM (7). A diferen�a m�dia por arquivo foi de 0.00 smells, o que indica uma discrep�ncia significativa entre as abordagens na detec��o em n�vel de arquivo.

### Quest�o 2: As duas abordagens convergem ou divergem nos resultados?

A taxa de similaridade entre as abordagens foi de 11.76%, indicando uma **alta diverg�ncia** entre os resultados. Das 5 categorias analisadas, 0 apresentaram alta sobreposi��o (>80%) e 5 apresentaram baixa sobreposi��o (<20%).

### Quest�o 3: Existem categorias de smells mais detectadas por cada abordagem?

A LLM detectou mais frequentemente smells da categoria **Long Method** com 2 ocorr�ncias. O SonarQube detectou mais frequentemente smells da categoria **Exception Handling** com 6 ocorr�ncias.

A categoria com maior diverg�ncia entre as abordagens foi **Duplicate Code**, com 100.00% de detec��es exclusivas somadas.

## Recomenda��es

Com base na an�lise realizada, recomenda-se:

1. **Abordagem complementar**: Utilizar ambas as ferramentas em conjunto, j� que apresentam uma taxa de similaridade de apenas 11.76%, complementando-se na detec��o.

2. **Foco em categorias espec�ficas**: A LLM mostrou maior efic�cia na detec��o de smells do tipo **Long Method**, enquanto o SonarQube se destacou em **Exception Handling**. Considerar essa especializa��o ao escolher a ferramenta adequada.

3. **Valida��o humana**: Para as categorias com baixa sobreposi��o entre as ferramentas, � recomendada uma revis�o manual para validar os resultados e identificar os falsos positivos.

4. **Refinamento de prompts**: Os resultados sugerem oportunidades para aprimorar a engenharia de prompts para as LLMs, especialmente nas categorias onde o SonarQube se mostrou mais eficaz.


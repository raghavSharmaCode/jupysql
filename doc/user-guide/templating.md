---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Templating

```{code-cell} ipython3
%pip install jupysql duckdb duckdb-engine --quiet
%load_ext sql
%sql duckdb://
```

```{code-cell} ipython3
from urllib.request import urlretrieve

_ = urlretrieve(
    "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
    "penguins.csv",
)
```

```{code-cell} ipython3
%%sql
SELECT *
FROM penguins.csv
LIMIT 3
```

```{code-cell} ipython3
%%sql
SELECT island, COUNT(*)
FROM penguins.csv
GROUP BY island
```

```{code-cell} ipython3
island = "Torgersen"
```

```{code-cell} ipython3
%%sql
SELECT DISTINCT(island)
FROM penguins.csv
WHERE island = '{island}'
```

## testing the existing templating feature

```{code-cell} ipython3
island = "Biscoe"
```

```{code-cell} ipython3
%%sql
SELECT DISTINCT(island)
FROM penguins.csv
WHERE island = '{island}'
```

## issue: inconsistent behavior

parameters can usse '{something}', :something, and $something but they behave differently and it's confusing when to use which. let's use jinja2.Template instead.

```{code-cell} ipython3
%%sql
SELECT DISTINCT(island)
FROM penguins.csv
WHERE island = :island
```

```{code-cell} ipython3
%%sql
SELECT DISTINCT(island)
FROM penguins.csv
WHERE island = $island
```

```{code-cell} ipython3
%%sql
SELECT DISTINCT(island)
FROM penguins.csv
WHERE island = '$island'
```

## issue: once the statement is rendered, the values won't change

Unsure why this is happennig but once I store a query:

```{code-cell} ipython3
%%sql --save one_island  --no-execute
SELECT *
FROM penguins.csv
WHERE island = '{island}'
```

changing the parameter won't re-render it. e.g., I'd expect the following to fail:

```{code-cell} ipython3
island = "not a valid island"
%sqlplot boxplot --table one_island --column body_mass_g --with one_island
```

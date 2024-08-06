# pgQuack

Our internal postgres proxy solution inspired by Josh' Wills' fantastic work with buenavista (https://github.com/jwills/buenavista)

# Getting started

```
python -m vinyl.infra.pg_proxy.server
```

Then in a separate terminal you can test it's working with:

```
psql -h 0.0.0.0  -p 5433 -c "show tables;"
```

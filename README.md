# Diskuze API Flask

Solution to IT Academy project

## First starting the project

Setup the environment

```sh
poetry install
poetry shell
```

Run local server

```sh
flask --app diskuze:app run
```

Open GraphiQL on address http://127.0.0.1:5000/graphql and run the test query

```graphql
{
  hello
  total
}
```

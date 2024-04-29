# Django database fixtures to dump and upload them

## Explanation:
To dump from existing db:

```shell
python manage.py dumpdata app_name.ModelName --indent 2 > fixtures/fixture_file.json
```

To load fixtures to db:

```shell
python manage.py loaddata fixtures/fixture_file.json --app app_name.ModelName
```

## DrinkJoys example

### dump users:

users
```shell
python manage.py dumpdata accounts.User --indent 2 > fixtures/users.json
```

### load users:
```shell
python manage.py loaddata fixtures/users.json --app accounts.User
```


# Frequently Used Before Release

Fixtures for main parts are usually used after dropping db.

> Note has to be made that after release, NEVER, ABSOLUTELY NEVER drop db. After that part if models will be anyhow changed, it is necessary to `makemigrations` and `migrate` them properly.

to dump:
```shell
python manage.py dumpdata accounts.User --indent 2 > fixtures/users.json
python manage.py dumpdata menu.Category --indent 2 > fixtures/categories.json
python manage.py dumpdata establishments.Establishment --indent 2 > fixtures/establishments.json
python manage.py dumpdata menu.Menu --indent 2 > fixtures/menus.json
python manage.py dumpdata menu.Beverage --indent 2 > fixtures/beverages.json
```

to load:
```shell
python manage.py loaddata fixtures/users.json --app accounts.User
python manage.py loaddata fixtures/categories.json --app menu.Category
python manage.py loaddata fixtures/establishments.json --app establishments.Establishment
python manage.py loaddata fixtures/menus.json --app menu.Menu
python manage.py loaddata fixtures/beverages.json --app menu.Beverage
```


# Notes on GIT and branches

To delete branch locally
```shell
git branch -d localBranchName
```

To delete branch remotely
```shell
git push origin --delete remoteBranchName
```

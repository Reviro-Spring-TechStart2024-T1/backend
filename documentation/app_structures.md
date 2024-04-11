# Single app structure
```bash
backend/ # example only
├── api/ # app that has all the main functionalities
│   ├── __init__.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── admin.py
│   ├── filters.py
│   ├── managers.py
│   ├── permissions.py
│   ├── serializers/
│   │   ├── __init__.py
│   │   ├── establishment.py
│   │   ├── user.py
│   │   └── beverage.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── establishment.py
│   │   ├── user.py
│   │   └── beverage.py
│   └── views/
│   │   ├── __init__.py
│   │   ├── establishment.py
│   │   ├── user.py
│   │   └── beverage.py
│   └── urls.py
├── core/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── common/
│   ├── __init__.py
│   ├── constants.py
│   ├── custom_logger.py
│   ├── exceptions.py
│   ├── filters.py
│   ├── generics.py
│   ├── messages.py
│   ├── mixins.py
│   ├── models.py
│   ├── pagination.py
│   ├── permissions.py
│   ├── swagger.py
│   ├── utils.py
│   └── viewsets.py
├── tests/
│   ├── test_models.py
│   └── test_views.py
├── .dockerignore
├── .gitignore
├── .env.example
├── Dockerfile
├── docker-compose.yaml
├── manage.py
└── requirements.txt
```

# Multiple app structure ✅
```bash
backend/ # example only
│
├──config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
│
├── apps/
│   ├── users/ # app name
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── views.py
│   │   └── serializers.py
│   │
│   ├── establishments/  # app name
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── views.py
│   │   └── serializers.py
│   │
│   ├── beverages/  # app name
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── views.py
│   │   └── serializers.py
│   │
│   ├── orders/  # app name
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── views.py
│   │   └── serializers.py
│   │
│   ├── qr_codes/  # app name
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── views.py
│   │   └── serializers.py
│   │
│   └── new added features/
└── utils/
│   ├── __init__.py
│   ├── permissions.py
│   └── helpers.py
│
├── .dockerignore
├── .gitignore
├── .env.example
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```

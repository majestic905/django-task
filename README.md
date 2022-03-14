# Launch services

```shell
docker compose -f docker-compose.prod.yml up -d --build
```

Navigate to http://localhost:8000/group/1 and check all is up and working

# Launch tests
```shell
docker compose exec web pytest -s
```

# Launch performance test

Current setup at test/locustfile.py uses a sample of 100 groups

```shell
pip install locust
cd test
locust
```

1) Navigate to http://0.0.0.0:8089/
2) Specify
   1) Number of users = 200
   2) Spawn rate = 5
   3) Host **(notice slash at the end of url)** = http://localhost:8000/ 

When finished navigate to http://localhost:8000/group to check that (up to) 100 groups were actually fetched

# Watch celery beat working
```shell
docker compose logs 'celery'
docker compose logs 'celery-beat'
```

Schedule is configured inside app/hello_django/settings.py
# Launch services

```shell
docker compose -f docker-compose.prod.yml up -d --build
```

Navigate to http://localhost:1337/group/1 and check all is up and working

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
   3) Host **(notice slash at the end of url)** = http://localhost:1337/ 

When finished navigate to http://localhost:1337/admin to check that (up to) 100 groups were actually fetched. Login/password is **root**/**root**.

# Watch celery beat working
```shell
docker compose logs 'celery'
docker compose logs 'celery-beat'
```

Also check updated_at column at http://localhost:1337/admin
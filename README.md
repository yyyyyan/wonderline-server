# Wonderline Server
A server who provides RESTFul APIs for [Wonderline UI](https://github.com/yyyyyan/wonderline-ui).
## Setup
 1. Creating virtual environment
    1. [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
    2. Create Python 3.7 virtual environment via Pycharm
        1. Open `preferences`, search `Python Interpreter`
        2. Click the configuration icon, then click the button `Add...`
        3. Click the `Conda Enviroment` on the left, choose `Python 3.7` as the Python version.
        4. Click `OK` and `Apply`.
    3. Activate virtual environment
        ```shell script
        conda activate wonderline-server
        ```
 2. Installing required libraries
    ```shell script
    brew install postgresql
    pip install -r requirements.txt
    ```
### Quick Start
**Using Docker**
 1. Install latest [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).
 2. Run the following command:
    ```shell script
    docker-compose rm -f && docker-compose up --build
    ```
 3. Wait every component (Flask, Minio, Cassandra, Nginx) to launch.
 6. The swagger documentations (empty now) are shown in [http://localhost](http://localhost).

**Troubleshooting**
 - Unable to launch postgres:
   ```shell script
   postgres          | initdb: directory "/var/lib/postgresql/data" exists but is not empty
   postgres          | If you want to create a new database system, either remove or empty
   postgres          | the directory "/var/lib/postgresql/data" or run initdb
   postgres          | with an argument other than "/var/lib/postgresql/data".
   postgres exited with code 1
   ```
   Fix:
   ```commandline
   rm -rf /tmp/postgres_data /tmp/minio_data /tmp/cassandra_data
   ```


### Debugging Cassandra
Open another terminal window, run the following command:
```shell script
docker run -ti --network wonderline-server_wonderline-shared-net --rm cassandra:3.11.6 cqlsh cassandra
```
You are expected to see a CQL Shell as follows:
```shell script
Connected to MyCluster at cassandra:9042.
[cqlsh 5.0.1 | Cassandra 3.11.6 | CQL spec 3.4.4 | Native protocol v4]
Use HELP for help.
cqlsh>
```

Test the following things:
 1. Change `keyspace`
    ```shell script
    USE wonderline;
    ```
 2. List all tables
    ```shell script
    DESCRIBE TABLES;
    ```
 3. List the contents for some tables:
    ```shell script
    SELECT * FROM user;
    SELECT * FROM photo;
    SELECT * FROM trip;
    SELECT * FROM trips_by_user;
    SELECT * FROM photos_by_trip;
    ```
### Debugging PostgreSQL
```shell script
docker run -ti --network wonderline-server_wonderline-shared-net --rm postgres:9.6.18 psql --host=postgres --username=wonderline_postgres
```

Test the following things:
 1. Change database
    ```
    \c wonderline
    ```
 2. Show user table
    ```
    select * from _user;
    ```
 3. Show following and followed tables
    ```
    select * from following;
    select * from followed;
    ```
### Debugging Flask
```shell script
export FLASK_ENV=development
export FLASK_APP=wonderline_app
flask run --port 8000
```
Open [http://localhost:8000](http://localhost:8000) to debug Swagger documentations.
### Debugging Minio
#### Minio Web Interface
Please follow the steps in `Quick Start`, then go to `http://localhost:9000/minio/photos/`,
it's a web interface showing all the files stored in the `photos` bucket.

#### Using minio client within the minio container
```shell script
docker run --net=wonderline-server_wonderline-shared-net -it --entrypoint=/bin/sh minio/mc
```
```shell script
mc config host add minio http://minio:9000 AKIAIOSFODNN7EXAMPLE wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
mc policy get minio/photos
mc ls minio/photos
```
#### How to make https work for minio
##### Generate private/public keys
```bash
openssl req -x509 -out public.crt -keyout private.key \
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nC=FR\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
```
##### Move them into a local folder
```bash
mkdir -p ./minio/certs
mv public.crt private.key ./minio/certs/
```
##### Setup docker-compose
```yaml
minio:
    container_name: minio
    image: minio/minio:RELEASE.2022-03-05T06-32-39Z.fips
    networks:
      - wonderline-shared-net
    ports:
      - 9000:9000
      - 9001:9001
    volumes:
      - /tmp/minio_data:/export
      - ./minio:/root/.minio
    environment:
      - MINIO_ROOT_USER=wonderline
      - MINIO_ROOT_PASSWORD=wonderline
      - MINIO_SERVER_URL=https://localhost:9000
    command: server --address ":9000" --console-address ":9001" /export
```
where `- minio:/root/minio`, `- MINIO_SERVER_URL=https://localhost:9000` and `--address ":9000" --console-address ":9001"`
are essential.
##### Change minio client code
```python
import os
import urllib3
from minio import Minio


minio_client = Minio(
    endpoint=os.environ['MINIO_HOST'] + ':' + os.environ['MINIO_PORT'],
    access_key=os.environ['MINIO_ROOT_USER'],
    secret_key=os.environ['MINIO_ROOT_PASSWORD'],
    secure=True,
    http_client=urllib3.PoolManager(cert_reqs="CERT_NONE"),
)
```

## Testing
Install the required libraries for testing
```shell script
pip install -r requirements.dev.txt
```
### Integration testing
 1. Launch all the containers
 ```shell script
 docker-compose rm -f && docker-compose up --build
 ```
 2. Open another new terminal
 ```shell script
 docker-compose exec -T wonderline_app pytest -vvs tests
 ```
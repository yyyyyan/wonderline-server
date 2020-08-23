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
    select * from _uesr;
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
 pytest -svv tests
 ```
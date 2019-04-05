# CIDDS: A Configurable and Distributed DAG-based Distributed Ledger Simulation Framework

[CIDDS: A Configurable and Distributed DAG-based Distributed Ledger Simulation Framework](https://dl.acm.org/citation.cfm?id=3284018)

Blockchain based distributed ledgers is one of the most studied research areas, owing to the enormous success of crypto-currencies like Bitcoin, Ethereum, etc. But, in addition to all the advantages, Blockchain is by design resource intensive and in general does not scale well. Hence, researchers all over are looking for alternatives for blockchain and one such alternative is the Tangle, introduced by IOTA foundation. Tangle is a Directed Acyclic Graph (DAG) based distributed ledger, which boasts advantages like high scalability and support for micro-payments. But outside the context of IOTA, the properties of a DAG-based distributed ledger are not studied. Also IOTA currently does not contain a large scale peer-to-peer simulation system with configurable parameters, which allows the users to study the important characteristics and metrics of the network and compare di erent scenarios under controlled conditions. This thesis proposes CIDDS, a Configurable and Interactive DAG based Distributed ledger Simulation framework as a solution to this problem. Using CIDDS, users can create large scale tangle simulations with thousands of nodes and study the characteristics of the resulting DAG ledgers with varying parameters.

# Documentation

[For detailed documentation, please review this Master Thesis](https://github.com/i13-msrg/cidds/blob/master/CIDDS_Thesis.pdf)


## Getting Started

This is a django project. To run this locally, please have all the dependencies required to run django. The following links can be followed to have django installed in the local machine.


* [Docs](https://docs.djangoproject.com/en/2.1/topics/install/) - Django Installation documentation
* [Sample](https://realpython.com/django-setup/) - In depth tutorial

And we use postgres database. Please install and setup a postgres database from the link below:
* [Download Postgres](https://www.postgresql.org/download/)

Once postgres is installed, create a database with the following parameters:

```
        'NAME': "cidds",
        'USER': "postgres",
        'PASSWORD': "postgres",
        'PORT': '5432',
        'HOST': 'localhost',
```


### Installation Instructions

Once the basic setup is complete, please follow these steps to run the server:


*  Clone this repository by running

```
git clone https://github.com/i13-msrg/cidds.git
```


*  Create Python 3 virtual environment named "venv"

```
virtualenv -p python3 venv
```



*  Activate the venv

```
source venv/bin/activate

```

*  Navigate to the directory cidds

```
cd cidds
```

* Install all the requirements

```
pip install -r requirements.txt
```

* Migrate the database 

```
python manage.py migrate
```
If the database is installed properly, this should create all the required tables for the application to run

* Now the application can be run by the following command

```
python manage.py runserver
```

## Accessing CIDDS online: 

CIDDS can be accessed online using the following link:
http://131.159.52.52:8080

## Inspirations from:

Please do visit these repositories for similar simulators:

* [IOTA Simulation](https://github.com/iotaledger/iotavisualization) 
* [Tangle Simulator](https://github.com/minh-nghia/TangleSimulator) 



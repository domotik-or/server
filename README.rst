Installing matplotlib
=====================

https://github.com/mesonbuild/meson/issues/14313#issuecomment-2814392556

.. code-block:: console

    pip install matplotlib
    --config-settings=setup-args=--cross-file=/home/domotik/server/src/meson_cross_file
    --break-system-packages

Packages to install
===================

Update the package list:

.. code-block:: console

    sudo apt-get update

For the Sqlite3 database:

.. code-block:: console

    sudo apt install sqlite3

For the Postgresql database:

.. code-block:: console

    sudo apt install postgresql

Clone the repository
====================

.. code-block:: console

    git clone git@gitlab-snfbo.com:boble/domotik/serveur/server.git
    cd server

Postgressql database setup
==========================

**Note**: in order for the postgresql authentication to work, you may have to
change the authentication method from *peer* to *scram-sha-256* in PostgreSQL
`pg_hba.conf` configuration file for all users except postgres user.

Change `postgres` user's password:

.. code-block:: console

    sudo -u postgres psql
    ALTER USER postgres with encrypted password 'your_password';
    exit

Create a database domotik user:

.. code-block:: console

    createuser -U postgres -W --pwprompt --createdb domotik
    Enter password for new role:
    Enter it again:

Drop the database if it exists:

.. code-block:: console

    dropdb -U domotik -W domotik

Create the database:

.. code-block:: console

    createdb -U domotik -W domotik

Create the tables in the domotik database:

.. code-block:: console

    psql -U domotik domotik < database/schema.sql

Application setup
=================

If necessary, use a virtual Python environment:

.. code-block:: console

    python3 -m venv .venv --prompt server --upgrade-deps
    source .venv/bin/activate

.. code-block:: console

    pip install .

Launch the server: ::

.. code-block:: console

    $ gunicorn server.main:app --bind 127.0.0.1:8080 --workers 3 --worker-class aiohttp.GunicornWebWorker

Testing the server
==================

.. code-block:: console

    wget -O - "localhost:8080"
    wget -O - "localhost:8080/set_east?value=2300000"
    wget -O - "localhost:8080/set_event?name=ring
    wget -O - "localhost:8080/set_outdoor?humidity=50&temperature=2400&pressure=97400
    wget -O - "localhost:8080/set_sinsts?value=230
    wget -O - "localhost:8080/set_temperature_humidity?temperature=2300&humidity=5100
    wget -O - "localhost:8080/datetime

    "/pressure/image"
    "/sinsts/image"
    "/temperature_humidity/image/{name}"

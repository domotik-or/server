Installing matplotlib
=====================

https://github.com/mesonbuild/meson/issues/14313#issuecomment-2814392556

.. code-block:: console

    pip install matplotlib
    --config-settings=setup-args=--cross-file=/home/domotik/server/src/meson_cross_file
    --break-system-packageso

Packages to install
===================

Update the package list:

.. code-block:: console

    sudo apt-get update

For the database:

.. code-block:: console

    sudo apt install postgresql

Clone the repository
====================

.. code-block:: console

    git clone git@gitlab-snfbo.com:boble/domotik/serveur/server.git
    cd server

Database setup
==============

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

    python3 -m venv .venv --prompt server --upgrade-deps --break-package-system
    source .venv/bin/activate

.. code-block:: console

    pip install -r requirements.txt

Launch the server: ::

.. code-block:: console

    $ gunicorn domotik.main:app --bind 127.0.0.1:8080 --workers 3 --worker-class aiohttp.GunicornWebWorker

Testing the server
==================

Getting the zone
----------------

.. code-block:: console

    wget -O - "localhost:8080/get_zone?longitude=0.8955510136151068&latitude=45.98346591051388"

Deleting battery event records
------------------------------

.. code-block:: console

    wget -O - --method=DELETE "localhost:8080/battery?zone_id=1&start_date=1743152400&end_date=1743580800"

Deleting navigation records
---------------------------

.. code-block:: console

    wget -O - --method=DELETE "localhost:8080/navigation?zone_id=1&start_date=1743152400&end_date=1743580800"

Deleting water quality records
------------------------------

.. code-block:: console

    wget -O - --method=DELETE "localhost:8080/water_quality?zone_id=1&start_date=1743152400&end_date=1743580800"

Getting battery event records
-----------------------------

.. code-block:: console

    wget -O - "localhost:8080/battery?zone_id=1&start_date=1743152400&end_date=1743580800"

Getting navigation records
--------------------------

.. code-block:: console

    wget -O - "localhost:8080/navigation?zone_id=1&start_date=1743152400&end_date=1743580800"

Getting water quality records
-----------------------------

.. code-block:: console

    wget -O - "localhost:8080/navigation?zone_id=1&start_date=1743152400&end_date=1743580800"

Sending battery event
---------------------

.. code-block:: console

    wget -q - localhost:8080/battery --post-data='{"zone_id": 1, "datetime": 1742893217, "event": 1}'

Sending navigation informations
-------------------------------

.. code-block:: console

    wget -q - localhost:8080/navigation --post-data='{"zone_id": 1, "datetime": 1742893217, "latitude": 45.98346591051388, "longitude": 0.8955510136151068, "depth": 1.1}'

Sending navigation informations
-------------------------------

.. code-block:: console

    wget -q - localhost:8080/water_quality --post-data='{"zone_id": 1, "datetime": 1742893217, "longitude": 0.8955510136151068, "latitude": 45.98346591051388, "barometric_pressure": 1013.25,"temperature": 21, "ph": 7, "oxydation_reduction_potential": 0.1, "electrical_conductivity": 0.2, "electrical_conductivity_20": 0.3, "electrical_conductivity_25": 0.4, "electrical_resistivity": 0.5, "salinity": 0.6, "total_dissolved_solids": 0.8, "specific_seawater_gravity": 0.9, "dissolved_oxygen": 1.1, "dissolved_oxygen_airsat": 1.2}'


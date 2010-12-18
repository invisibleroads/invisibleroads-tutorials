Install GeoDjango
=================
Here you will install GeoDjango, a framework for building web-based mapping applications.  We first presented this tutorial as part of a three-hour session on `Working with Geographic Information Systems in Python <http://us.pycon.org/2009/tutorials/schedule/1PM4/>`_ during the `2009 Python Conference <http://us.pycon.org/2009/>`_ in Chicago, Illinois.

.. raw:: html

    <object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/Nte3hYohhYQ&hl=en&fs=1&rel=0"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/Nte3hYohhYQ&hl=en&fs=1&rel=0" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>


Walkthrough for Fedora
----------------------
Become the superuser
::
    
    su


Install Django
^^^^^^^^^^^^^^
Download and install the latest version of `Django <http://www.djangoproject.com>`_.
::

    svn co http://code.djangoproject.com/svn/django/trunk/ django
    cd django
    python setup.py install


Install geospatial libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Install through the graphical interface or the command line.
::

    yum install gdal gdal-python geos proj


Install `PostgreSQL <http://www.postgresql.org>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Install through the graphical interface or the command line.
::

    yum install postgresql postgresql-devel postgresql-server python-psycopg2

Initialize the PostgreSQL database and start the service.
::

    service postgresql initdb
    service postgresql start

Change postgres password.
::

    passwd postgres


Configure `PostgreSQL <http://www.postgresql.org>`_ permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The default configuration of PostgreSQL requires authentication through two accounts for each user: a Linux account and a PostgreSQL account.  PostgreSQL starts with a default PostgreSQL superuser account with the username *postgres*.

If you want to create and access PostgreSQL databases, you will either need to create a PostgreSQL account for a Linux account or you need to change the default configuration.  The relevant configuration is contained in the ``pg_hba.conf`` file.

Open ``pg_hba.conf``.
::

    su - postgres
    cd data
    vim pg_hba.conf


.. _postgresql-default:

Default configuration
"""""""""""""""""""""
Here is the default configuration, in which *ident sameuser* indicates that a Linux user can only sign into a PostgreSQL account that has the same username as the user's Linux account.  
::

    # "local" is for Unix domain socket connections only
    local   all         all                               ident sameuser
    # IPv4 local connections:
    host    all         all         127.0.0.1/32          ident sameuser
    # IPv6 local connections:
    host    all         all         ::1/128               ident sameuser

You can create a PostgreSQL account using the *createuser* command.
::
    
    createuser


.. _postgresql-alternate:

Alternate configuration
"""""""""""""""""""""""

Here is an alternate configuration, in which *trust* indicates that a Linux user can sign into any PostgreSQL account.
::

    # "local" is for Unix domain socket connections only
    local   all         all                               trust
    # IPv4 local connections:
    host    all         all         127.0.0.1/32          trust
    # IPv6 local connections:
    host    all         all         ::1/128               trust

Remember to restart the service after changing the configuration.
::

    su
    service postgresql restart


Install `PostGIS <http://postgis.refractions.net>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Install through the graphical interface or the command line.
::

    yum install postgis


Verify the paths of the SQL files; note that the file locations for 32-bit and 64-bit systems are different.
::

    find `pg_config --sharedir` | grep lwpostgis
    find `pg_config --sharedir` | grep spatial_ref_sys

`Create a spatial database template on a 32-bit system <http://geodjango.org/docs/install.html#spatialdb-template>`_.
::

    su - postgres
    createdb -E UTF8 template_postgis
    createlang -d template_postgis plpgsql
    psql -d template_postgis -f /usr/share/pgsql/contrib/lwpostgis.sql
    psql -d template_postgis -f /usr/share/pgsql/contrib/spatial_ref_sys.sql
    psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"

`Create a spatial database template on a 64-bit system <http://geodjango.org/docs/install.html#spatialdb-template>`_.
::

    su - postgres
    createdb -E UTF8 template_postgis
    createlang -d template_postgis plpgsql
    psql -d template_postgis -f /usr/share/pgsql/contrib/lwpostgis-64.sql
    psql -d template_postgis -f /usr/share/pgsql/contrib/spatial_ref_sys.sql
    psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"


Start project
^^^^^^^^^^^^^
To create a new PostGIS database, use the following command and replace *databaseUser* with an existing username and replace *databaseName* with the desired name of the database.
::

    createdb -T template_postgis -U postgres -O databaseUser databaseName

You can now start working through the `GeoDjango tutorial <http://geodjango.org/docs/tutorial.html>`_.

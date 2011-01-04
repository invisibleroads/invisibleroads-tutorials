Install PostGIS
===============
`PostGIS <http://postgis.refractions.net/>`_ is a spatial extension module for `PostgreSQL <http://www.postgresql.org/>`_.


Install packages
^^^^^^^^^^^^^^^^
Install packages through the graphical interface or the command line, then initialize and start the PostgreSQL database service.
::

    su
        yum -y install postgresql postgresql-devel postgresql-server python-psycopg2 postgis
        service postgresql initdb
        service postgresql start


Enable *trust* authentication for configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In *trust* authentication, a Linux user may sign into any PostgreSQL user account without a password prompt.  The *trust* authentication method is useful when you want to reset PostgreSQL usernames and passwords, but it is not secure for deployment.

PostgreSQL user accounts are separate from Linux user accounts and may be set with different passwords even though they may share the same username.  Log in as the database administrator *postgres* to control which PostgreSQL users have access to a database and what actions the PostgreSQL user may perform on the database.

If you cannot log in as the Linux user *postgres*, reset the password.  The Linux account is used to modify PostgreSQL settings.
::

    su
        passwd postgres

If you cannot log in as the PostgreSQL user *postgres*, reset the password.  The PostgreSQL account is used to manage PostgreSQL databases.
::

    su - postgres
        vim data/pg_hba.conf
            # "local" is for Unix domain socket connections only
            local   all         all                               trust
            # IPv4 local connections:
            host    all         all         127.0.0.1/32          trust
            # IPv6 local connections:
            host    all         all         ::1/128               trust
    su
        service postgresql restart
        psql -U postgres -c "alter role postgres with password 'SET-PASSWORD-HERE';"
        service postgresql restart


Prepare a spatial database template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Note that the SQL file locations are different between 32-bit and 64-bit systems.  You may want to temporarily enable *trust* authentication as described above if you do not want to enter your *postgres* password multiple times.
::

    su - postgres
        createdb -E UTF8 template_postgis
        createlang -d template_postgis plpgsql
        PGSHARE=`pg_config --sharedir`
        PGSQL=`find $PGSHARE -name postgis.sql -o -name postgis-64.sql | tail -n 1`
        PGSQLSP=`find $PGSHARE -name spatial_ref_sys.sql | tail -n 1`
        psql -d template_postgis -f $PGSQL
        psql -d template_postgis -f $PGSQLSP
        psql -d template_postgis -c 'grant all on geometry_columns to public;'
        psql -d template_postgis -c 'grant all on spatial_ref_sys to public;'


Enable *md5* authentication for deployment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A secure option for accessing PostgreSQL databases is via *md5* authentication, which requires you to create a PostgreSQL user with a password and grant the user access to specific databases.
::

    su - postgres
        vim data/pg_hba.conf
            # "local" is for Unix domain socket connections only
            local   all         all                               md5
            # IPv4 local connections:
            host    all         all         127.0.0.1/32          md5
            # IPv6 local connections:
            host    all         all         ::1/128               md5
    su
        service postgresql restart

A more secure option is *ident sameuser* authentication, in which the PostgreSQL user must have the same username as the Linux user who is trying to access the database.


Manage PostgreSQL users
^^^^^^^^^^^^^^^^^^^^^^^
Create a PostgreSQL user with limited privileges.
::

    createuser -U postgres SET-USERNAME-HERE -S -D -R
    psql -U postgres -c "alter role SET-USERNAME-HERE with password 'SET-PASSWORD-HERE';"

Drop a PostgreSQL user.
::

    dropuser -U postgres SET-USERNAME-HERE

Grant database privileges (not necessary if the user is the database owner).
::

    psql -c "grant all on database SET-DATABASE-HERE to SET-USERNAME-HERE;"

Revoke database privileges.
::

    psql -c "revoke all on database SET-DATABASE-HERE from SET-USERNAME-HERE;"


Manage PostgreSQL databases
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create a regular database and set its owner.
::

    createdb -U postgres -O SET-USERNAME-HERE SET-DATABASE-HERE

Create a spatial database and set its owner.
::

    createdb -U postgres -T template_postgis -O SET-USERNAME-HERE SET-DATABASE-HERE

Reset a spatial database.
::

    dropdb -U postgres SET-DATABASE-HERE
    createdb -U postgres -T template_postgis -O SET-USERNAME-HERE SET-DATABASE-HERE

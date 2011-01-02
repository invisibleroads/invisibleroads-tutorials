Install PostGIS
===============
`PostGIS <http://postgis.refractions.net/>`_ is a spatial extension module for `PostgreSQL <http://www.postgresql.org/>`_.


Install PostgreSQL
^^^^^^^^^^^^^^^^^^
Install packages through the graphical interface or the command line, then initialize and start the PostgreSQL database service.
::

    su
        yum -y install postgresql postgresql-devel postgresql-server python-psycopg2
        service postgresql initdb
        service postgresql start

Set the password for the Linux user *postgres*.  The Linux account is used to modify PostgreSQL settings.
::

    su
        passwd postgres

Set the password for the PostgreSQL user *postgres*.  The PostgreSQL account is used to manage PostgreSQL databases.
::

    psql -U postgres -c "alter role postgres with password 'SET-PASSWORD-HERE';"


Configure PostgreSQL permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PostgreSQL user accounts are separate from Linux user accounts and may be set with different passwords even though they may share the same username.  Log in as the database administrator *postgres* to control which PostgreSQL users have access to a database and what actions the PostgreSQL user may perform on the database.

If you cannot log in as the Linux user *postgres*, you can reset the password.
::

    su
        passwd postgres

If you cannot log in as the PostgreSQL user *postgres*, you can reset the password.
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

One option for accessing PostgreSQL databases securely is via *md5* authentication, which requires you to create a PostgreSQL user with a password and grant the user access to specific databases.
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

Other options include *ident sameuser* authentication, in which the PostgreSQL user must have the same username as the Linux user who is trying to access the database, and *trust* authentication, in which a Linux user may sign into any PostgreSQL account without a password prompt.  The *trust* authentication method is useful when you have forgotten and want to reset PostgreSQL usernames and passwords.

Here are various commands for administering PostgreSQL user accounts.
::
    
    su - postgres
        # Create PostgreSQL user
        createuser SET-USERNAME-HERE
        # Set password
        psql -c "alter role SET-USERNAME-HERE with password 'SET-PASSWORD-HERE';"
        # Create database and set its owner
        createdb -O SET-USERNAME-HERE SET-DATABASE-HERE
        # Grant database privileges (not necessary if the user is the owner)
        psql -c "grant all on database SET-DATABASE-HERE to SET-USERNAME-HERE;"
        # Revoke database privileges
        psql -c "revoke all on database SET-DATABASE-HERE from SET-USERNAME-HERE;"
        # Drop PostgreSQL user
        dropuser SET-USERNAME-HERE


Install PostGIS
^^^^^^^^^^^^^^^
Install PostGIS through the graphical interface or the command line.
::

    yum -y install postgis

Prepare a spatial database template.  Note that the SQL file locations are different between 32-bit and 64-bit systems.  You may want to temporarily enable *trust* authentication if you do not want to enter your *postgres* password multiple times.
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


Manage a sample PostGIS database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create a PostgreSQL user.
::

    createuser -U postgres SET-USERNAME-HERE
    psql -U postgres -c "alter role SET-USERNAME-HERE with password 'SET-PASSWORD-HERE';"

Create a spatial database.
::

    createdb -U postgres -T template_postgis -O SET-USERNAME-HERE SET-DATABASE-HERE

Reset the database.
::

    dropdb -U postgres SET-DATABASE-HERE
    createdb -U postgres -T template_postgis -O SET-USERNAME-HERE SET-DATABASE-HERE

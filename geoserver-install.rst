Install GeoServer
=================
Here you will install GeoServer, a server for map images and location data.  We first presented this tutorial as part of a three-hour session on `Working with Geographic Information Systems in Python <http://us.pycon.org/2009/tutorials/schedule/1PM4/>`_ during the `2009 Python Conference <http://us.pycon.org/2009/>`_ in Chicago, Illinois.

.. raw:: html

    <object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/deffK7Vkm00&hl=en&fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/deffK7Vkm00&hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>


Walkthrough for Fedora
----------------------
Download `GeoServer <http://geoserver.org>`_


Test GeoServer
^^^^^^^^^^^^^^
Set JAVA_HOME environment variable
::
    
    export JAVA_HOME=/usr/lib/jvm/jre/

Unzip and run ``bin/startup.sh``
::
    
    unzip geoserver-1.7.3a-bin.zip
    cd geoserver-1.7.3/bin
    ./startup.sh

Go to http://localhost:8080/geoserver


Install GeoServer to load at boot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Copy geoserver files to ``/usr/local/geoserver``
::
   
    su
    cp -R geoserver-1.7.3 /usr/local/geoserver

Add the following lines to the end of ``/etc/rc.local``
::

    export JAVA_HOME=/usr/lib/jvm/jre/
    export GEOSERVER_HOME=/usr/local/geoserver/
    /usr/local/geoserver/bin/startup.sh &


Troubleshoot errors
-------------------
Some users have reported problems setting the JAVA_HOME environment variable.  In particular, you may be getting the following error on trying to run the ``startup.sh`` script.
::

    The JAVA_HOME environment variable is not defined
    This environment variable is needed to run this program

In these cases you will need to find the location of the JRE (Java Runtime Environment).  Make sure that the JRE contains the ``bin`` and ``lib`` subfolders.
::

    su            # Login as root
    updatedb      # Update database
    locate jre    # Locate the Java Runtime Library

The default setup for Fedora 11 64-bit has the following preset shortcuts, which may help you find the JRE on your system.
::

    /usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86_64
    /usr/lib/jvm/jre                               -> /etc/alternatives/jre
    /usr/lib/jvm/jre-1.6.0                         -> /etc/alternatives/jre_1.6.0
    /usr/lib/jvm/jre-1.6.0-openjdk.x86_64          -> java-1.6.0-openjdk-1.6.0.0.x86_64/jre
    /usr/lib/jvm/jre-openjdk                       -> /etc/alternatives/jre_openjdk
    /etc/alternatives/jre                          -> /usr/lib/jvm/jre-1.6.0-openjdk.x86_64
    /etc/alternatives/jre_1.6.0                    -> /usr/lib/jvm/jre-1.6.0-openjdk.x86_64
    /etc/alternatives/jre_openjdk                  -> /usr/lib/jvm/jre-1.6.0-openjdk.x86_64

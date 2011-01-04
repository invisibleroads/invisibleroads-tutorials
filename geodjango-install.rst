Install GeoDjango
=================
Here you will install GeoDjango, a framework for building web-based mapping applications.  We first presented this tutorial as part of a three-hour session on `Working with Geographic Information Systems in Python <http://us.pycon.org/2009/tutorials/schedule/1PM4/>`_ during the `2009 Python Conference <http://us.pycon.org/2009/>`_ in Chicago, Illinois.

.. raw:: html

    <object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/Nte3hYohhYQ&hl=en&fs=1&rel=0"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/Nte3hYohhYQ&hl=en&fs=1&rel=0" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>


Walkthrough for Fedora
----------------------


Install Django
^^^^^^^^^^^^^^
Download and install the latest version of `Django <http://www.djangoproject.com>`_.
::

    su
        svn co http://code.djangoproject.com/svn/django/trunk/ django
        python django/setup.py install
        rm -Rf django


Install geospatial libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Install through the graphical interface or the command line.
::

    su
        yum -y install gdal gdal-python geos proj


Install PostGIS
^^^^^^^^^^^^^^^
See :doc:`postgresql-postgis-install`


Start project
^^^^^^^^^^^^^
You can now start working through the `GeoDjango tutorial <http://docs.djangoproject.com/en/dev/ref/contrib/gis/tutorial/>`_.

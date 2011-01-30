Connect two computers running Fedora Linux via ethernet
=======================================================


Connect the computers
---------------------
Option 1: Plug the computers into the same router.

Option 2: Connect the computers using a crossover cable.


Assign IP addresses
-------------------
Make sure that both computers have IP addresses and share the same netmask.
::

    ifconfig eth0

If a computer does not have an IP address, you must assign one.  In the following example, we are assigning the computer an IP address of ``192.168.10.10`` using netmask ``255.255.255.0`` over ethernet device ``eth0``.  Remember that both computers must have different IP addresses and the same netmask.
::

    su
        ifconfig eth0 192.168.10.10 netmask 255.255.255.0 up

You can have a computer assign itself a static IP through the NetworkManager applet.
::

    Edit Connections 
        Wired 
            Add
                IPv4 Settings 
                    Method: Manual 
                    Add 
                        Address: 192.168.10.10 
                        Netmask: 255.255.255.0 
                        Gateway: 192.168.10.1


Start SSH server on host
------------------------
Start the SSH server daemon on the computer that you want to access remotely.
::

    su
        service sshd start

You can have the SSH server start automatically every time you restart the computer by enabling the service.  The easiest way to do this is by installing ``system-config-services``, selecting ``sshd`` and clicking Enable.
::

    su
        yum -y install system-config-services


Open SSH port in firewall on host
---------------------------------
Even though you might see SSH checked in ``system-config-firewall``, the port might not actually be open.  Uncheck and check SSH, then click Apply.  The following line should be visible when you run ``iptables-save`` as root.
::

    -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT 


SSH into the host
-----------------
Here we SSH into the computer with IP address 192.168.10.10 with agent key and trusted X11 forwarding.  Key forwarding passes the SSH keys of our client computer so that we can access our Git repositories.  X11 forwarding lets us run programs on the host computer that require an X11 graphical display.
::

    ssh -A -Y 192.168.10.10

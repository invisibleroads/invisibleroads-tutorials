Install Fedora 19 to dual boot Windows 8.1 on Vaio Pro
======================================================
After following the steps in this guide, you will have installed Fedora 19 to dual boot Windows 8.1 on a Vaio Pro Ultrabook.  Thanks to `Nick Brackley <http://www.nicksplace.com.au>`_ for his initial work in getting Fedora 19 working on the Vaio Pro.  Thanks to `Pascal C <http://www.nicksplace.com.au/2013/07/01/sony-vaio-pro-13-vs-fedora-19/#comment-61>`_ for suggesting the use of `bcdedit`.

Boot Fedora 19 from live usb
----------------------------
- Make Vaio recovery disks.
- Install `liveusb-creator <https://fedorahosted.org/liveusb-creator/>`_.
- Make Fedora 19 live usb.
- Create shutdown shortcut tile.

    - Press Windows-d to see the desktop.
    - Right-click on the desktop and choose New > Shortcut.
    - Specify "shutdown /s /t 0" as the command.
    - Right-click on the shortcut and choose Properties.
    - Choose an icon for the shortcut.
    - Pin shortcut to the start screen.

- Shutdown.
- Press the ASSIST button to enter BIOS.
- Disable Secure Boot.
- Boot Fedora 19 live usb.

Install Fedora 19
-----------------
- Press the windows button, type "terminal" and press ENTER
- Mount the EFI partition.

    sudo mount /dev/sda1 /home/liveuser/Templates

- Backup the original EFI configuration.

    cd Templates
    tar czvf ../EFI-original.tar.gz *
    sudo umount /home/liveuser/Templates

- Save the original EFI configuration to a second usb drive.
- Start the Fedora 19 installation wizard.
- Choose standard partition (not LVM).
- Resize the Windows partition.
- Determine Fedora partition automatically.
- Delete the automatically created /boot/efi partition.
- Set /dev/sda1 to mount point /boot/efi.
- Set /dev/sda1 to EFI System Partition.
- Do not format /dev/sda1 (although if you do, you can just restore your EFI backup).
- Install Fedora 19.
- Do not reboot yet.

Configure EFI
-------------
- Mount the EFI partition.

    sudo mount /dev/sda1 /home/liveuser/Templates

- Copy and extract the original EFI configuration.

    cd /home/liveuser/Templates
    tar xzvf EFI-original.tar.gz 

- Rearrange your EFI folder structure so that it looks like the following.

    /EFI/Boot/bootx64.efi (original)
    /EFI/Fedora/shim.efi
    /EFI/Microsoft/Boot/bootmgfw.efi (original)

- Update grub to add the Windows Boot Manager.

    cd /home/liveuser/Templates/EFI/Fedora
    grub2-mkconfig -o grub.cfg

- Reboot (Windows will start).
- Press Windows-x a to open an administrative terminal.
- Update Windows Boot Configuration Data.

    bcdedit /set {bootmgr} path \EFI\Fedora\shim.efi

- Download necessary RPMs and patches from `Nix Adventures <http://www.nicksplace.com.au>`_.  Note that if you have a smartphone with USB tethering, then you will not need Nick's RPMs.
- Click the shutdown tile or run the following command.

    shutdown /s /t 0

Boot Fedora 19 from hard drive
------------------------------
- Reboot (Fedora should start).
- Tether your smartphone's internet connection.
- Update the system and halt.

    yum -y update
    sudo halt

- Press the ASSIST button to enter BIOS.
- Enable Secure Boot.

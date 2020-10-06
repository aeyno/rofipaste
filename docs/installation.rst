.. highlight:: shell

Installation
============

Dependencies
------------

RofiPaste depends on `rofi`_, `FontAwesome`_ and xdotool

.. _rofi: https://github.com/davatorium/rofi
.. _FontAwesome: https://fontawesome.com/

Installing dependencies
-----------------------

Debian / Ubuntu / Linux Mint / Elementary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ sudo apt-get install rofi fonts-font-awesome xdotool

.. todo::

    Update instructions for font-awesome (the version from apt isn't up to date)

Arch / Manjaro
~~~~~~~~~~~~~~

.. code-block:: console

    $ sudo pacman -Suy rofi xdotool
    $ git clone https://aur.archlinux.org/ttf-font-awesome-4.git
    $ cd ttf-font-awesome-4
    $ makepkg -si


Fedora
~~~~~~

.. code-block:: console

    $ sudo dnf install rofi xdotool


.. todo::

    Add instructions for font-awesome



Stable release
--------------

To install RofiPaste, run this command in your terminal:

.. code-block:: console

    $ pip install rofipaste

This is the preferred method to install RofiPaste, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for RofiPaste can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/Any0ne22/rofipaste

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/Any0ne22/rofipaste/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/Any0ne22/rofipaste
.. _tarball: https://github.com/Any0ne22/rofipaste/tarball/master

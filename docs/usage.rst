=====
Usage
=====

To launch RofiPaste from the command line simply type ``rofipaste``
Once you've set your paste files, bind a keyboard shortcut to RofiPaste to access the content of your file from everywhere.



Configure rofipaste
-------------------

When you lanch rofipaste for the first time, a configuration file is created at ``~/.config/rofipaste/config``.

All the options are already presents and commented, if you want to edit something you just have to remove the ``#`` in front of the line.

To edit the config file with your default editor, you can also just type ``rofipaste --edit-config`` or by launching rofipaste and launching the config edition.

Set up your pastes
------------------

If you want to create an entry for rofipaste, you can just use the following command:

.. code-block:: bash

  rofipaste --edit-entry

Then, you will have to enter the name of your file, for instance ``my_python_snippets/my_awesome_python_code.py``

If your filename ends by ``.py`` or anything else, then, the extension will be removed when printed in rofipaste and there will be an icon in front of the entry.

If you type a relative path with some folders, then those folders will be created if necessary and your entry will be in this folder.


Create a dynamic paste
----------------------

A dynamic paste is just a script which is executed when selected in rofipaste, and the output *(stdout)* will be pasted. The difference with a *classic* paste is the presence of a **shebang**.

An exemple is a good way to understand the concept:

.. code-block:: bash

    #!/bin/bash
    date


If you create this paste, when you will use it the script will be executed by **/bin/bash** and the *stdout* (the date here) will be pasted.

A good way to create dynamic pastes is to use the clipboard as an entry. For instance, you can create an entry which paste your clipboard in CAPS LOCK:

.. code-block:: python

  #!/bin/python3

  from rofipaste import get_clipboard_content as gcp
  print(gcp().upper())


Shortcuts
---------

When you are in rofipaste, you can use some shortcuts to perform different actions

.. list-table:: 
  :widths: 35 65
  :header-rows: 1

  * - Shortcut
    - Action
  * - Ctrl+C
    - Just copy (don't paste)
  * - Alt+p
    - Copy paste (instead of typing)
  * - Alt+e
    - Edit the selected file



Commands
--------

You can type some commands in rofipaste.

.. list-table:: 
  :widths: 35 65
  :header-rows: 1

  * - Command
    - Action
  * - /config
    - Edit the config file


More informations
-----------------

If you want more informations about the usage of rofipaste, you can check the *help* page by typing ``rofipaste --help``.

You will discover some new arguments that allow you to only copy the pastes for instance.

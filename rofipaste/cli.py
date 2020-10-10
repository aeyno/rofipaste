"""Console script for rofipaste."""
import sys
import os
from xdg import BaseDirectory
import click
import click_config_file
from pathlib import Path
from rofipaste import rofipaste, __version__

config_file_name: str = rofipaste.config_file_name

default_config = """##################################
##     Default config file      ##
## Uncomment the lines you want ##
##################################

## Use your clipboard to copy paste things instead of just typing it (recommanded on Wayland and for non qwerty keyboards)
# insert_with_clipboard=True                # Default: False

## Just copy the 'paste' content
# copy_only=True                            # Default: False

## Use a different folder than the default one for storing your pastes
# files="/home/<my username>/my pastes"    # Default: /home/<my username>/.local/share/rofipaste/pastes_folder

## Use a different prompt in rofi
# prompt="This is my custom prompt"         # Default: "Rofipaste ❤ "

## Give rofi some arguments
# rofi_args=""                              # Default: ""

## Use your favorite editor
# editor="subl"                             # This is for sublime text
# editor="vscode"                           # Visual Studio Code
# editor="termite -e 'nvim $FILE'"          # nvim with termite
"""


def createIfNotExist(path):
    """
    Create a directory if it doesn't exists
    """
    Path(path).mkdir(parents=True, exist_ok=True)


@click.command()
@click.option('--version',
              default=False,
              help='Print the current version',
              is_flag=True)
@click.option(
    '--edit-config',
    default=False,
    help='Open your default terminal editor to edit your config file',
    is_flag=True)
@click.option(
    '--edit-entry',
    default=False,
    help=
    'Open your default terminal editor to edit one of your paste entry (or create a new one)',
    is_flag=True)
@click.option(
    '-p',
    '--insert-with-clipboard',
    default=False,
    help=
    'Do not type the characters directly, but copy it to the clipboard, insert it from '
    'there and then restore the clipboard\'s original value',
    is_flag=True)
@click.option(
    '-c',
    '--copy-only',
    default=False,
    help='Only copy the characters to the clipboard but do not insert it',
    is_flag=True)
@click.option('-f',
              '--files',
              default='pastes_folder',
              help='Read pastes from this directory')
@click.option('-r',
              '--prompt',
              default='Rofipaste ❤ ',
              help='Set rofipaste\'s  prompt')
@click.option('--rofi-args',
              default='',
              help='A string of arguments to give to rofi')
@click.option('-e',
              '--editor',
              default='none',
              help='path to your favorite editor')
@click_config_file.configuration_option(config_file_name=config_file_name)
def main(version: bool, edit_config: bool, edit_entry: bool,
         insert_with_clipboard: bool, copy_only: bool, files: str, prompt: str,
         rofi_args: str, editor: str) -> int:
    """
    RofiPaste is a tool allowing you to copy / paste pieces of codes or other useful texts
    """

    filesPath: str = os.path.join(BaseDirectory.xdg_data_home, 'rofipaste',
                                  files)

    config_dirname = os.path.dirname(config_file_name)
    if not os.path.isdir(config_dirname):
        os.makedirs(config_dirname)
    if not os.path.isfile(config_file_name):
        with open(config_file_name, 'w') as config_file:
            config_file.write(default_config)

    if edit_config:
        rofipaste.edit_file(config_file_name, editor, xdg_open=True)
        return 0

    if edit_entry:
        filename = click.prompt('Please enter the filename',
                                default="new_entry")

        filename = os.path.join(filesPath, filename)

        dirname = os.path.dirname(filename)

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        if not os.path.isfile(filename):
            os.mknod(filename)

        rofipaste.edit_file(filename, editor)
        return 0

    if version:
        click.echo(f"Current version: {__version__}")
        return 0

    Action = rofipaste.Action
    action = {
        True: Action.TYPE,
        insert_with_clipboard: Action.INSERT_WITH_CLIPBOARD,
        copy_only: Action.COPY_ONLY,
    }[True]

    active_window = rofipaste.get_active_window()
    if filesPath[-1] == "/":
        #Removing / at the end to avoid base_folder different from current_folder when going back to top folder
        filesPath = filesPath[:-1]
    createIfNotExist(filesPath)
    base_folder = filesPath
    current_folder = base_folder

    while True:
        folder_content = rofipaste.read_folder_content(current_folder)

        if current_folder != base_folder:
            folder_content = f'{rofipaste.undo_icon} ..\n' + folder_content

        returncode, stdout = rofipaste.open_main_rofi_window(
            rofi_args.split(" "), folder_content, prompt)

        if returncode == 1:
            return 0

        if (stdout[0] == rofipaste.command_prefix):
            rofipaste.commandInterpreter(stdout.rstrip('\n'), editor)
            return 0

        splitted = stdout.rstrip('\n').split(' ')
        icon, path = splitted[0], os.path.join(
            current_folder, ' '.join(splitted[1:]).replace(' (exec)', ''))

        if icon == rofipaste.folder_icon:
            current_folder = path

        elif icon == rofipaste.undo_icon:
            current_folder = os.path.dirname(current_folder)

        elif icon == rofipaste.edit_config_icon:
            rofipaste.edit_file(config_file_name, editor, xdg_open=True)
            return 0

        elif icon in rofipaste.paste_icon_dict.values():
            path = path.rstrip()

            path += '.' + {y: x
                           for x, y in rofipaste.paste_icon_dict.items()}[icon]

            if path[-1] == '.':
                path = path[:-1]

            if 10 <= returncode <= 19:
                # TODO: create shortcuts with 0-9 keys
                #default_handle_recent_character(returncode - 9,  active_window)
                return 0
            else:
                data = rofipaste.fileInterpreter(path)
                if returncode == 0:
                    rofipaste.default_handle(data, action, active_window)
                elif returncode == 20:
                    rofipaste.copy_characters_to_clipboard(data)
                elif returncode == 21:
                    rofipaste.type_characters(data, active_window)
                elif returncode == 22:
                    rofipaste.copy_paste_characters(data, active_window)
                elif returncode == 23:
                    #Alt+e opens edit mode
                    rofipaste.edit_file(path, editor)
                return 0
        else:
            return -1

    return 0

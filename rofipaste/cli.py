"""Console script for rofipaste."""
import sys
import os
from xdg import BaseDirectory
import click
import click_config_file
from rofipaste import rofipaste

__version__ = '0.1.2'


@click.command()
@click.option('--version',
              default=False,
              help='Print the current version',
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
@click.option(
    '--max-recent',
    default=10,
    help=
    'Show at most this number of recently used characters (cannot be larger than 10)'
)
@click_config_file.configuration_option(config_file_name=os.path.join(
    BaseDirectory.xdg_config_home, 'rofipaste/config'))
def main(version: bool, insert_with_clipboard: bool, copy_only: bool,
         files: str, prompt: str, rofi_args: str, max_recent: int) -> int:
    """
    RofiPaste is a tool allowing you to copy / paste pieces of codes or other useful texts
    """

    if version:
        click.echo(f"Current version: {__version__}")
        return 0

    filesPath: str = os.path.join(BaseDirectory.xdg_data_home, 'rofipaste',
                                  files)

    Action = rofipaste.Action
    action = {
        True: Action.TYPE,
        insert_with_clipboard: Action.INSERT_WITH_CLIPBOARD,
        copy_only: Action.COPY_ONLY
    }[True]

    active_window = rofipaste.get_active_window()
    if filesPath[-1] == "/":
        #Removing / at the end to avoid base_folder different from current_folder when going back to top folder
        filesPath = filesPath[:-1]
    base_folder = filesPath
    current_folder = base_folder

    while True:
        folder_content = rofipaste.read_folder_content(current_folder)

        if current_folder != base_folder:
            folder_content = f'{rofipaste.undo_icon} ..\n' + folder_content

        returncode, stdout = rofipaste.open_main_rofi_window(
            rofi_args.split(" "), folder_content, prompt, max_recent)

        if returncode == 1:
            return 0

        splitted = stdout.rstrip('\n').split(' ')
        icon, path = splitted[0], os.path.join(current_folder,
                                               ' '.join(splitted[1:]))

        if icon == rofipaste.folder_icon:
            current_folder = path
        elif icon == rofipaste.undo_icon:
            current_folder = os.path.dirname(current_folder)
        elif icon in rofipaste.paste_icon_dict.values():
            path = path.rstrip(' (exec)')

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
                return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

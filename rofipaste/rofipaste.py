"""Main module."""

import os
from subprocess import run, CompletedProcess

from enum import Enum, auto

from typing import List, Tuple, Dict

import click

folder_icon: str = ""
undo_icon: str = ""
edit_config_icon: str = ""
paste_icon_dict: Dict[str, str] = dict(py="",
                                       js="",
                                       java="",
                                       html="",
                                       css="",
                                       c="C",
                                       cpp="C++",
                                       sh="")
paste_icon_dict[''] = ''


class Action(Enum):
    COPY_ONLY = auto()
    INSERT_WITH_CLIPBOARD = auto()
    TYPE = auto()

def read_folder_content(folder_path: str) -> str:
    """read_folder_content.
    
    Read the content of the specified folder and return the found entries

    :param folder_path: Folder's path
    :type folder_path: str
    :rtype: str
    """

    file_entries: str = ''
    exec_entries: str = ''
    dir_entries: str = ''

    for f in os.listdir(folder_path):
        filename = os.path.join(folder_path, f)
        if os.path.isfile(filename):
            with open(filename, 'r') as file_:
                firstline = file_.readline()
            extension = '.'.join(f.split('.')[1:])

            try:
                icon = paste_icon_dict[extension]
                entry_name = f.split('.')[0]
            except:
                icon = paste_icon_dict['']
                entry_name = f

            exec_entries += f'{icon} {entry_name}'

            if firstline[:2] == "#!":
                exec_entries += ' (exec)'

            exec_entries += '\n'
        else:
            dir_entries += f'{folder_icon} {f}\n'

    return (file_entries + exec_entries + dir_entries +
            f"{edit_config_icon} Edit configuration file\n")


def fileInterpreter(path: str) -> str:
    """fileInterpreter

    Interpret the specified file (according to its extension).

    :param path: File's path
    :type path: str
    :rtype: str
    """

    with open(path, 'r') as f:
        content: str = f.read()

    if content[:2] == "#!":
        shebang: str = content.split('\n')[0]
        output: str = run([shebang[2:], path],
                          capture_output=True,
                          encoding='utf-8').stdout
        return output

    return content


def get_active_window() -> str:
    """get_active_window.

    Return the id of the active window

    :rtype: str
    """

    return run(args=['xdotool', 'getactivewindow'],
               capture_output=True,
               encoding='utf-8').stdout[:-1]


def open_main_rofi_window(rofi_args: List[str], characters: str, prompt: str) -> Tuple[int, str]:
    parameters: List[str] = [
        'rofi', '-dmenu', '-markup-rows', '-i', '-multi-select', '-p', prompt,
        '-kb-custom-11', 'Alt+c', '-kb-custom-12', 'Alt+t', '-kb-custom-13',
        'Alt+p', *rofi_args
    ]

    # TODO: Remove "-multi-select" from the parameters ?

    parameters.extend(['-mesg', "Type :edit to edit your config file"])

    rofi: CompletedProcess = run(parameters,
                                 input=characters,
                                 capture_output=True,
                                 encoding='utf-8')

    return rofi.returncode, rofi.stdout


def default_handle(characters: str, action: Action,
                   active_window: str) -> None:
    """default_handle.

    :param characters: The caracters to paste
    :type characters: str
    :param action: The action to perform (paste / type ...)
    :type action: Action
    :param active_window: ID of the active window
    :type active_window: str
    :rtype: None
    """

    if action == Action.COPY_ONLY:
        copy_characters_to_clipboard(characters)

    elif action == Action.INSERT_WITH_CLIPBOARD:
        copy_paste_characters(characters, active_window)

    elif action == Action.TYPE:
        type_characters(characters, active_window)


def copy_characters_to_clipboard(characters: str) -> None:
    """copy_characters_to_clipboard.

    Copy the characters to the clipboard

    :param characters: Characters to copy
    :type characters: str
    :rtype: None
    """

    run(['xsel', '-i', '-b'], input=characters, encoding='utf-8')


def copy_paste_characters(characters: str, active_window: str) -> None:
    """copy_paste_characters.

    Insert characters by copying it and pasting it to the active window

    :param characters: Characters to paste
    :type characters: str
    :param active_window: ID of the active window
    :type active_window: str
    :rtype: None
    """

    old_clipboard_content: str = run(
        args=['xsel', '-o', '-b'], capture_output=True).stdout.decode("utf-8")
    old_primary_content: str = run(args=['xsel', '-o', '-p'],
                                   capture_output=True).stdout.decode("utf-8")

    run(args=['xsel', '-i', '-b'], input=characters, encoding='utf-8')
    run(args=['xsel', '-i', '-p'], input=characters, encoding='utf-8')

    run([
        'xdotool',
        'windowfocus',
        '--sync',
        active_window,
        'key',
        '--clearmodifiers',
        'Shift+Insert',
        'sleep',
        '0.05',
    ])

    run(args=['xsel', '-i', '-b'],
        input=old_clipboard_content,
        encoding='utf-8')
    run(args=['xsel', '-i', '-p'], input=old_primary_content, encoding='utf-8')


def type_characters(characters: str, active_window: str) -> None:
    """type_characters.

    Type the characters in the active window

    :param characters: Characters to type
    :type characters: str
    :param active_window: ID of the active window
    :type active_window: str
    :rtype: None
    """

    run(['xdotool', 'type', '--window', active_window, characters],
        encoding="utf-8")

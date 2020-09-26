#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import fnmatch
import os
import shlex
import sys
import json
from subprocess import run, PIPE
from typing import List, Tuple
import configargparse
from xdg import BaseDirectory


folder_icon: str = ""
paste_icon: str = ""
undo_icon: str = ""


def read_folder_content(folder_path: str) -> str:
    file_entries = ''
    dir_entries = ''

    for f in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, f)):
            file_entries += f'{paste_icon} {f}\n'
        else:
            dir_entries += f'{folder_icon} {f}\n'

    return file_entries + dir_entries


def fileInterpreter(path):
    fileExt = path.split(".")[-1]
    print(fileExt)
    if fileExt == "sh":
        cmd = run(["bash", path],capture_output=True,encoding='utf-8')
        return cmd.stdout
    else:
        f = open(path, 'r')
        content = f.read()
        f.close()
        return content


def main() -> None:
    args = parse_arguments()
    active_window = get_active_window()
    base_folder = args.files
    current_folder = base_folder

    print(base_folder)

    while True:
        folder_content = read_folder_content(current_folder)

        if current_folder != base_folder:
            folder_content = f'{undo_icon} ..\n' + folder_content
        
        returncode, stdout = open_main_rofi_window(
            args.rofi_args,
            folder_content,
            args.prompt,
            args.max_recent
        )

        if returncode == 1:
            sys.exit()
        
        splitted = stdout.rstrip('\n').split(' ')
        icon, path = splitted[0], os.path.join(current_folder,' '.join(splitted[1:]))

        if icon == folder_icon:
            current_folder = path
        elif icon == undo_icon:
            current_folder = os.path.dirname(current_folder)
        elif icon == paste_icon:
            if 10 <= returncode <= 19:
                # TODO: create shortcuts with 0-9 keys
                #default_handle_recent_character(returncode - 9, args, active_window)
                return
            else:
                data = fileInterpreter(path)
                if returncode == 0:
                    default_handle(data, args, active_window)
                elif returncode == 20:
                    copy_characters_to_clipboard(data)
                elif returncode == 21:
                    type_characters(data, active_window)
                elif returncode == 22:
                    copy_paste_characters(data, active_window)
                return


def parse_arguments() -> argparse.Namespace:
    parser = configargparse.ArgumentParser(
        description='Paste text using rofi.',
        default_config_files=[os.path.join(directory, 'rofipast.rc') for directory in
                              BaseDirectory.xdg_config_dirs]
    )
    parser.add_argument('--version', action='version', version='rofipaste 0.1')
    parser.add_argument(
        '--insert-with-clipboard',
        '-p',
        dest='insert_with_clipboard',
        action='store_true',
        help='Do not type the character directly, but copy it to the clipboard, insert it from '
             'there and then restore the clipboard\'s original value '
    )
    parser.add_argument(
        '--copy-only',
        '-c',
        dest='copy_only',
        action='store_true',
        help='Only copy the character to the clipboard but do not insert it'
    )

    parser.add_argument(
        '--files',
        '-f',
        dest='files',
        action='store',
        default= os.path.join(BaseDirectory.xdg_data_home, 'rofipaste/pastes_folder'),
        metavar='FILE',
        help='Read pastes from this directory'
    )
    parser.add_argument(
        '--prompt',
        '-r',
        dest='prompt',
        action='store',
        default='Rofipaste ❤ ',
        help='Set rofipast\'s  prompt'
    )
    parser.add_argument(
        '--rofi-args',
        dest='rofi_args',
        action='store',
        default='',
        help='A string of arguments to give to rofi'
    )
    parser.add_argument(
        '--max-recent',
        dest='max_recent',
        action='store',
        type=int,
        default=10,
        help='Show at most this number of recently used characters (cannot be larger than 10)'
    )

    parsed_args = parser.parse_args()
    parsed_args.rofi_args = shlex.split(parsed_args.rofi_args)

    return parsed_args


def get_active_window() -> str:
    return run(args=['xdotool', 'getactivewindow'], capture_output=True, encoding='utf-8').stdout[:-1]


def open_main_rofi_window(rofi_args: List[str], characters: str, prompt: str, max_recent: int) -> Tuple[int, str]:
    parameters = [
        'rofi',
        '-dmenu',
        '-markup-rows',
        '-i',
        '-multi-select',
        '-p',
        prompt,
        '-kb-custom-11',
        'Alt+c',
        '-kb-custom-12',
        'Alt+t',
        '-kb-custom-13',
        'Alt+p',
        *rofi_args
    ]

    
    parameters.extend(['-mesg', "Type :edit to edit your config file"])

    rofi = run(
        parameters,
        input=characters,
        capture_output=True,
        encoding='utf-8'
    )
    return rofi.returncode, rofi.stdout


def default_handle(characters: str, args: argparse.Namespace, active_window: str):
    if args.copy_only:
        copy_characters_to_clipboard(characters)
    elif args.insert_with_clipboard:
        copy_paste_characters(characters, active_window)
    else:
        type_characters(characters, active_window)


def copy_paste_characters(characters: str, active_window: str) -> None:
    old_clipboard_content = run(args=['xsel', '-o', '-b'], capture_output=True).stdout
    old_primary_content = run(args=['xsel', '-o', '-p'], capture_output=True).stdout

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

    run(args=['xsel', '-i', '-b'], input=old_clipboard_content)
    run(args=['xsel', '-i', '-p'], input=old_primary_content)


def type_characters(characters: str, active_window: str) -> None:
    '''Type the string characters on the current window'''
    run([
        'xdotool',
        'type',
        '--window',
        active_window,
        characters
    ], encoding="utf-8")


def copy_characters_to_clipboard(characters: str) -> None:
    run([
        'xsel',
        '-i',
        '-b'
    ],
        input=characters,
        encoding='utf-8'
    )


if __name__ == "__main__":
    main()

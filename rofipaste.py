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


thingsToPaste = []

def loadConfig(configFile):
    global thingsToPaste
    pastesFile = open("./pastes.json")
    thingsToPaste = json.loads(pastesFile.read())
    pastesFile.close()

def getThingsToPaste() -> str:
    params = [":edit"]
    for x in thingsToPaste:
        params.append(x["name"])
    return "\n".join(params)


def commandInterpreter(command):
    global thingsToPaste
    if(command == ":edit"):
        editConfig("./pastes.json")
        return ""
    else:
        for x in thingsToPaste:
            if x["name"] == command:
                if x["type"] == "text":
                    return x["value"]
                elif x["type"] == "command":
                    #TODO : regex to parse spaces in the command
                    cmd = run(x["value"].split(" "),capture_output=True,encoding='utf-8')
                    print(cmd.stdout)
                    return cmd.stdout

def editConfig(configFile):
    run(args=['vim', configFile,], encoding='utf-8')
    try:
        loadConfig(configFile)
        print("Changes saved !")
    except:
        print("Something is wrong with your file !")

def main() -> None:
    loadConfig("./pastes.json")
    args = parse_arguments()
    active_window = get_active_window()

    returncode, stdout = open_main_rofi_window(
        args.rofi_args,
        #read_character_files(args.files),
        getThingsToPaste(),
        args.prompt,
        args.max_recent
    )

    if returncode == 1:
        sys.exit()
    else:
        if 10 <= returncode <= 19:
            pass

            #default_handle_recent_character(returncode - 9, args, active_window)
        else:
            cmd = stdout.splitlines()[0]
            print(cmd)
            data = commandInterpreter(cmd)
            if returncode == 0:
                default_handle(data, args, active_window)
            elif returncode == 20:
                copy_characters_to_clipboard(data)
            elif returncode == 21:
                type_characters(data, active_window)
            elif returncode == 22:
                copy_paste_characters(data, active_window)


def parse_arguments() -> argparse.Namespace:
    parser = configargparse.ArgumentParser(
        description='Select, insert or copy Unicode characters using rofi.',
        default_config_files=[os.path.join(directory, 'rofimoji.rc') for directory in
                              BaseDirectory.xdg_config_dirs]
    )
    parser.add_argument('--version', action='version', version='rofimoji 4.2.0')
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
        '--skin-tone',
        '-s',
        dest='skin_tone',
        action='store',
        choices=['neutral', 'light', 'medium-light', 'moderate', 'dark brown', 'black', 'ask'],
        default='ask',
        help='Decide on a skin-tone for all supported emojis. If not set (or set to "ask"), '
             'you will be asked for each one '
    )
    parser.add_argument(
        '--files',
        '-f',
        dest='files',
        action='store',
        default=['emojis'],
        nargs='+',
        metavar='FILE',
        help='Read characters from this file instead, one entry per line'
    )
    parser.add_argument(
        '--prompt',
        '-r',
        dest='prompt',
        action='store',
        default='Rofipaste ❤ ',
        help='Set rofimoj\'s  prompt'
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
    #In order to type the characters using xdotool, we need to get the actual keyboard layout of the user
    # TODO: use "setxkbmap -query | grep layout" to get the layout
    t = run(['setxkbmap', 'fr'], stdout=PIPE)
    run([
        'xdotool',
        'type',
        '--window',
        active_window,
        characters
    ], input=t.stdout)


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

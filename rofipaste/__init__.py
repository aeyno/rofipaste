"""Top-level package for RofiPaste."""

__author__ = """Tom GOUVILLE / Lucas VALENTIN"""
__email__ = 'tom.gouville@telecomnancy.net / lucas.valentin@telecomnancy.net'
__version__ = '0.1.7'


def get_clipboard_content() -> str:
    from subprocess import run

    stdout: str = run(args=['xsel', '-o', '-b'],
                      capture_output=True,
                      encoding='utf-8').stdout
    return stdout

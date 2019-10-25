from colorama import Fore, Back, Style


def red(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.RED + brightness + txt + Style.RESET_ALL


def cyan(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.CYAN + brightness + txt + Style.RESET_ALL


def magenta(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.MAGENTA + brightness + txt + Style.RESET_ALL


def blue(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.BLUE + brightness + txt + Style.RESET_ALL


def yellow(txt, bright=False):
    brightness = bright and Style.BRIGHT or Style.NORMAL
    return Fore.YELLOW + brightness + txt + style.RESET_ALL

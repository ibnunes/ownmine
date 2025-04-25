"""# Escape library
Escape the ANSI Escape Code hellhole

* License: GNU-GPL v2.0

Igor Nunes, 2023
* Contribute in https://github.com/ibnunes/Escape
"""

from platform import system as get_os

class Ansi(object):
    """ Class to build ANSI Escape Codes (AEC)

    Attributes:
        * `ESCAPE_CODES` (dict): Conversion from readable string to AEC int.
        * `COLOR_MODE` (dict): Translates the number of colors to the appropriate mode (`5`: 8-bit; `2`: RGB).
    """

    ESCAPE_CODES = {
        'reset'                     : 0,
        'bold'                      : 1,
        'faint'                     : 2,
        'italic'                    : 3,
        'underline'                 : 4,
        'blink_slow'                : 5,
        'blink_rapid'               : 6,
        'reverse'                   : 7,
        'conceal'                   : 8,
        'crossout'                  : 9,
        'font_primary'              : 10,
        'font_alternate_1'          : 11,
        'font_alternate_2'          : 12,
        'font_alternate_3'          : 13,
        'font_alternate_4'          : 14,
        'font_alternate_5'          : 15,
        'font_alternate_6'          : 16,
        'font_alternate_7'          : 17,
        'font_alternate_8'          : 18,
        'font_alternate_9'          : 19,
        'fraktur'                   : 20,
        'bold_off'                  : 21,
        'underline_double'          : 21,
        'color_normal'              : 22,
        'italic_off'                : 23,
        'fraktur_off'               : 23,
        'underline_off'             : 24,
        'blink_off'                 : 25,
        'inverse_off'               : 27,
        'reveal'                    : 28,
        'crossout_off'              : 29,
        'fg_black'                  : 30,
        'fg_red'                    : 31,
        'fg_green'                  : 32,
        'fg_yellow'                 : 33,
        'fg_blue'                   : 34,
        'fg_magenta'                : 35,
        'fg_cyan'                   : 36,
        'fg_white'                  : 37,
        'fg'                        : 38,
        'fg_default'                : 39,
        'bg_black'                  : 40,
        'bg_red'                    : 41,
        'bg_green'                  : 42,
        'bg_yellow'                 : 43,
        'bg_blue'                   : 44,
        'bg_magenta'                : 45,
        'bg_cyan'                   : 46,
        'bg_white'                  : 47,
        'bg'                        : 48,
        'bg_default'                : 49,
        'frame'                     : 51,
        'encircle'                  : 52,
        'overline'                  : 53,
        'frame_off'                 : 54,
        'encircle_off'              : 54,
        'overline_off'              : 55,
        'ideogram_underline'        : 60,
        'ideogram_underline_double' : 61,
        'ideogram_overline'         : 62,
        'ideogram_overline_double'  : 63,
        'ideogram_stressmark'       : 64,
        'ideogram_off'              : 65,
        'fg_bright_black'           : 90,
        'fg_bright_red'             : 91,
        'fg_bright_green'           : 92,
        'fg_bright_yellow'          : 93,
        'fg_bright_blue'            : 94,
        'fg_bright_magenta'         : 95,
        'fg_bright_cyan'            : 96,
        'fg_bright_white'           : 97,
        'bg_bright_black'           : 100,
        'bg_bright_red'             : 101,
        'bg_bright_green'           : 102,
        'bg_bright_yellow'          : 103,
        'bg_bright_blue'            : 104,
        'bg_bright_magenta'         : 105,
        'bg_bright_cyan'            : 106,
        'bg_bright_white'           : 107
    }

    COLOR_MODE = {
        1 : "5",
        3 : "2"
    }


    @staticmethod
    def _canonize_color(color : int) -> int:
        """Internal function! Forces a color to be in the range [0, 255].\\
        If the color is greater than 255, it'll be capped to 255.\\
        If the color is under 0, it'll be corrected to 0.

        ### Parameters
            * `color` (int): a value representing a color.

        ### Return
            (int) An unsigned integral value in the range of [0, 255].
        """
        return color if color in range(0, 256) else (0 if color < 0 else 255)


    @staticmethod
    def escape(*args) -> str:
        """Builds an ANSI Escape Code from the given arguments.

        ### Parameters
            * `args` (any): should be a string as defined in `ESCAPE_CODES` and, in case of personalized colors (`fg`, `bg`), unsigned int values in the range [0, 255].

        ### Return
            (str) A ready-to-use ANSI Escape Code.
        """

        if get_os() not in ["Linux", "Darwin"]:
            return ""

        ESCAPE_FORMAT = "\033[§m"
        SEPARATOR     = ';'
        _catch        = False
        color         = []
        param         = []

        for arg in args:
            if arg in ['fg', 'bg']:
                if _catch:
                    param.append(Ansi.COLOR_MODE[len(color)])
                    param += color
                    color = []
                param.append(str(Ansi.ESCAPE_CODES[str(arg)]))
                _catch = True
            else:
                if _catch and str(arg).isdecimal():
                    color.append(str(Ansi._canonize_color(int(arg))))
                    continue
                elif _catch:
                    _catch = False
                    param.append(Ansi.COLOR_MODE[len(color)])
                    param += color
                    color = []
                param.append(str(Ansi.ESCAPE_CODES[str(arg)]))

        if color != []:
            param.append(Ansi.COLOR_MODE[len(color)])
            param += color

        ansi_code = SEPARATOR.join(param)
        return ESCAPE_FORMAT.replace("§", ansi_code if ansi_code != "" else "0")


if __name__ == "__main__":
    print("Hey! This is a library, my fello developer. I don't do a thing by myself :')")
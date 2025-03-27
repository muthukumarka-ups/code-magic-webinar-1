#!/usr/bin/env python3
"""Generate zsh completion script.

Usage
-----
.. code-block:: zsh
    scripts/zsh_completion.py
    sudo mv _[^_]* /usr/share/zsh/site-functions  # don't mv __pycache__
    rm -f ~/.zcompdump  # optional
    compinit  # regenerate ~/.zcompdump

Generate (from source code)
---------------------------
# Move pdd from project directory to auto-completion/zsh/pdd.py
# Run: ./zsh_completion.py

Debug
-----
.. code-block:: zsh
    scripts/zsh_completion.py MODULE_NAME -  # will output to stdout

Refer
-----
- https://github.com/ytdl-org/youtube-dl/blob/master/devscripts/zsh-completion.py
- https://github.com/zsh-users/zsh/blob/master/Etc/completion-style-guide

Examples
--------
.. code-block::
    '(- *)'{-h,--help}'[show this help message and exit]'
    |<-1->||<---2--->||<---------------3--------------->|

.. code-block:: console
    % foo --<TAB>
    option
    --help      show this help message and exit
    % foo --help <TAB>
    no more arguments

.. code-block::
    --color'[When to show color. Default: auto. Support: auto, always, never]:when:(auto always never)'
    |<-2->||<------------------------------3------------------------------->||<4>||<--------5-------->|

.. code-block:: console
    % foo --color <TAB>
    when
    always
    auto
    never

.. code-block::
    --color'[When to show color. Default: auto. Support: auto, always, never]:when:((auto\:"only when output is stdout" always\:always never\:never))'
    |<-2->||<------------------------------3------------------------------->||<4>||<--------------------------------5------------------------------->|

.. code-block:: console
    % foo --color <TAB>
    when
    always   always
    auto     only when output is stdout
    never    never

.. code-block::
    --config='[Config file. Default: ~/.config/foo/foo.toml]:config file:_files -g toml'
    |<--2-->||<---------------------3--------------------->||<---4---->||<-----5------>|

.. code-block:: console
    % foo --config <TAB>
    config file
    a.toml  b/
    ...

.. code-block::
    {1,2}'::_command_names -e'
    |<2->|4|<-------5------->|

.. code-block:: console
    % foo help<TAB>
    _command_names -e
    help2man  generate a simple manual page
    helpviewer
    ...
    % foo hello hello <TAB>
    no more arguments

.. code-block::
    '*: :_command_names -e'
    2|4||<-------5------->|

.. code-block:: console
    % foo help<TAB>
    external command
    help2man  generate a simple manual page
    helpviewer
    ...
    % foo hello hello help<TAB>
    external command
    help2man  generate a simple manual page
    helpviewer
    ...

+----+------------+----------+------+
| id | variable   | required | expr |
+====+============+==========+======+
| 1  | prefix     | F        | (.*) |
| 2  | optionstr  | T        | .*   |
| 3  | helpstr    | F        | [.*] |
| 4  | metavar    | F        | :.*  |
| 5  | completion | F        | :.*  |
+----+------------+----------+------+
"""
from argparse import (
    FileType,
    SUPPRESS,
    _HelpAction,
    _SubParsersAction,
    _VersionAction,
)
import os
from os.path import dirname as dirn
import sys
from typing import Final, Tuple

path = dirn(dirn(dirn(os.path.abspath(__file__))))
sys.path.insert(0, path)
PACKAGE: Final = "pdd" if sys.argv[1:2] == [] else sys.argv[1]
parser = __import__(PACKAGE).get_parser()
actions = parser._actions
BINNAME: Final = PACKAGE.replace("_", "-")
BINNAMES: Final = [BINNAME]
ZSH_COMPLETION_FILE: Final = (
    "_" + BINNAME if sys.argv[2:3] == [] else sys.argv[2]
)
ZSH_COMPLETION_TEMPLATE: Final = os.path.join(
    dirn(os.path.abspath(__file__)), "zsh_completion.in"
)
SUPPRESS_HELP = SUPPRESS
SUPPRESS_USAGE = SUPPRESS

flags = []
position = 1
for action in actions:
    if action.__class__ in [_HelpAction, _VersionAction]:
        prefix = "'(- *)'"
    elif isinstance(action, _SubParsersAction):  # TODO
        raise NotImplementedError
    else:
        prefix = ""

    if len(action.option_strings) > 1:  # {} cannot be quoted
        optionstr = "{" + ",".join(action.option_strings) + "}'"
    elif len(action.option_strings) == 1:
        optionstr = action.option_strings[0] + "'"
    else:  # action.option_strings == [], positional argument
        if action.nargs in ["*", "+"]:
            optionstr = "'*"  # * must be quoted
        else:
            if isinstance(action.nargs, int) and action.nargs > 1:
                old_position = position
                position += action.nargs
                optionstr = ",".join(map(str, range(old_position, position)))
                optionstr = "{" + optionstr + "}'"
            else:  # action.nargs in [1, None, "?"]:
                optionstr = str(position) + "'"
                position += 1

    if (
        action.help
        and action.help != SUPPRESS_HELP
        and action.option_strings != []
    ):
        helpstr = action.help.replace("]", "\\]").replace("'", "'\\''")
        helpstr = "[" + helpstr + "]"
    else:
        helpstr = ""

    if isinstance(action.metavar, str):
        metavar = action.metavar
    elif isinstance(action.metavar, Tuple):
        metavar = " ".join(map(str, action.metavar))
        # need some changes in template file
    else:  # action.metavar is None
        if action.nargs == 0:
            metavar = ""
        elif action.option_strings == []:
            metavar = action.dest
        elif isinstance(action.type, FileType):
            metavar = "file"
        elif action.type:
            metavar = action.type.__name__
        else:
            metavar = action.default.__class__.__name__
    if metavar != "":
        # use lowcase conventionally
        metavar = metavar.lower().replace(":", "\\:")

    if action.choices:
        completion = "(" + " ".join(map(str, action.choices)) + ")"
    elif metavar == "file":
        completion = "_files"
        metavar = " "
    elif metavar == "dir":
        completion = "_dirs"
        metavar = " "
    elif metavar == "url":
        completion = "_urls"
        metavar = " "
    elif metavar == "command":
        completion = "_command_names -e"
        metavar = " "
    else:
        completion = ""

    if metavar != "":
        metavar = ":" + metavar
    if completion != "":
        completion = ":" + completion

    flag = "{0}{1}{2}{3}{4}'".format(
        prefix, optionstr, helpstr, metavar, completion
    )
    flags += [flag]

with open(ZSH_COMPLETION_TEMPLATE) as f:
    template = f.read()

template = template.replace("{{programs}}", " ".join(BINNAMES))
template = template.replace("{{flags}}", " \\\n  ".join(flags))

with (
    open(ZSH_COMPLETION_FILE, "w")
    if ZSH_COMPLETION_FILE != "-"
    else sys.stdout
) as f:
    f.write(template)


from datetime import datetime, timedelta
import calendar

def date_difference(date1, date2):
    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def time_difference(time1, time2):
    t1 = datetime.strptime(time1, "%H:%M:%S")
    t2 = datetime.strptime(time2, "%H:%M:%S")
    return abs((t2 - t1))

def weeks_between_dates(date1, date2):
    return date_difference(date1, date2) // 7

def days_between_dates(date1, date2):
    return date_difference(date1, date2)

def count_sundays(start_date, end_date):
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    count = 0
    while d1 <= d2:
        if d1.weekday() == 6:
            count += 1
        d1 += timedelta(days=1)
    return count

def working_days_between(start_date, end_date):
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    count = 0
    while d1 <= d2:
        if d1.weekday() < 5:  # Monday to Friday
            count += 1
        d1 += timedelta(days=1)
    return count

# Example Usage
d1 = "2023-01-01"
d2 = "2023-12-31"
print("Date Difference:", date_difference(d1, d2))
print("Time Difference:", time_difference("12:30:00", "14:45:00"))
print("Weeks Between Dates:", weeks_between_dates(d1, d2))
print("Days Between Dates:", days_between_dates(d1, d2))
print("Number of Sundays:", count_sundays(d1, d2))
print("Working Days Between:", working_days_between(d1, d2))

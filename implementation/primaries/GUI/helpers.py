import os
import sys
import inspect


def get_base_dir(return_this_dir=False):
    if getattr(sys, "frozen", False):
        # If this is running in the context of a frozen (executable) file,
        # we return the path of the main application executable
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # If we are running in script or debug mode, we need
        # to inspect the currently executing frame. This enable us to always
        # derive the directory of main.py no matter from where this function
        # is being called
        thisdir = os.path.dirname(inspect.getfile(inspect.currentframe()))
        parent = os.path.abspath(os.path.join(thisdir, os.pardir))
        if return_this_dir:
            return thisdir
        else:
            return parent


def parseStyle(stylesheet, theme, theme_folder):
    results = []
    for line in stylesheet:
        cleaned_line = cleanPath(line)
        themed_path = parseThemePath(cleaned_line, theme_folder)
        finished_path = parseIconPath(themed_path, theme)
        results.append(finished_path)
    return "".join(results)


def cleanPath(path):
    path_to_parse = path
    if sys.platform == 'win32':
        path_to_parse = path.replace('/', '\\')
    return path_to_parse


def parseThemePath(path, theme_folder):
    path_to_parse = path
    prefix = ''
    postfix = ''
    parsed_path = path
    if 'themes' in path_to_parse:
        while 'themes' in path_to_parse:
            split_path = os.path.split(path_to_parse)
            if split_path[0] != 'themes':
                prefix = split_path[0]
            if postfix == '':
                postfix = split_path[1]
            elif split_path[1] != 'themes':
                postfix = os.path.join(split_path[1], postfix)
            path_to_parse = split_path[0]
        if '(' in prefix:
            parsed_path = prefix
        else:
            parsed_path = ''
        if sys.platform == 'win32':
            parsed_path += '\''
        parsed_path = parsed_path + theme_folder
        if sys.platform == 'win32':
            end_path = postfix.split(')')
            if len(end_path) > 1:
                parsed_path = os.path.join(
                    parsed_path, end_path[0]) + "')" + end_path[1]
            else:
                parsed_path = os.path.join(parsed_path, postfix) + "'"
        else:
            parsed_path = os.path.join(parsed_path, postfix)
    return parsed_path


def parseIconPath(path, theme):
    prefix = ''
    postfix = ''
    parsing_path = path
    parsed_path = path
    if 'icons' in parsing_path:
        while 'icons' in parsing_path:
            split_path = os.path.split(parsing_path)
            if postfix == '' and split_path != 'icons':
                postfix = split_path[1]
            elif split_path[1] != 'icons':
                postfix = os.path.join(split_path[1], postfix)
            if 'icons' not in split_path[0]:
                prefix = split_path[0]
            parsing_path = split_path[0]
        parsed_path = os.path.join(prefix, 'icons', theme, postfix)
    return parsed_path


def postProcessLines(lines):
    return_val = lines.replace('\\', '/')
    return return_val


def merge_instruments(instrument_list):
    return ", ".join([instrument["name"] for instrument in instrument_list])


def merge_clefs_and_keys(clef_or_key_dict):
    result = ''
    for instrument in clef_or_key_dict:
        result += ", ".join(clef_or_key_dict[instrument])
    return result


def fit_columns_to_widget(widget, columns):
    for column in range(columns):
        widget.setColumnWidth(column, widget.width() / (columns - 1))

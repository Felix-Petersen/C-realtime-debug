#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C-realtime-debug

use example:
python3 
"""

__author__      = "Felix Petersen"
__copyright__   = "Copyright 2017, Felix Petersen"
# __license__     = ""
__version__     = "2017.11.13"
__email__       = "mail@felix-petersen.de"
__status__      = "Production"

import sys, os, re
import argparse
import time

counter_variable_name_counter = 0

header_comment = "/*\n" \
                 " * DEBUG by CRealtimeDebug.py\n" \
                 " * All debug lines can be removed using the same script.\n" \
                 " * \n" \
                 " * CRealtimeDebug by Felix Petersen\n" \
                 " * Copyright (c) 2017 Felix Petersen. All rights reserved.\n" \
                 " */\n"
debug_str1 = "/*DEBUG by CRealtimeDebug.py*/"
debug_str2 = "/*DEBUG by CRealtimeDebug.py | Please do NOT write anything into this line*/"

# TODO: ensure that for/while/if etc. is not part of var name etc.

def get_count_init_line():
    global counter_variable_name_counter
    counter_variable_name_counter += 1
    return debug_str1 + "  int cRealtimeDebugInt" + str(counter_variable_name_counter) + " = 0;  " + debug_str2
def get_count_line():
    return debug_str1 + "  cRealtimeDebugInt" + str(counter_variable_name_counter) + "++;  " + debug_str2
def get_debug_line(parantheses_content, type):
    output = debug_str1
    output += 'std::cout << "[' + args.input_file_dir + '][" << __FUNCTION__ << "][Line " << __LINE__ << "] Loop Type: ' + type
    output += ', condition: (' + parantheses_content + '), count: " << cRealtimeDebugInt' + str(counter_variable_name_counter) + ';  '
    output += debug_str2
    return output
def get_debug_line_without_count(parantheses_content, type):
    output = debug_str1
    output += 'std::cout << "[' + args.input_file_dir + '][" << __FUNCTION__ << "][Line " << __LINE__ << "] Cond Type: ' + type
    output += ', condition: (' + parantheses_content + '), value: " << (' + parantheses_content + ');  '
    output += debug_str2
    return output

def run_state_machine_add(content):
    pos = -1
    # for debugging:
    # begin = 2750
    line = 1
    char = ''
    line_add_count = 0
    eol_comment = False
    block_comment = False
    single_quotes = False
    double_quotes = False
    in_type = False
    search_parantheses = -1
    search_braces = -1
    parantheses_start = 0
    parantheses_content = ''
    if_start = 0
    short_without_braces = False
    short_without_braces_found = False
    with_braces_found = False
    do_while_found_while = False
    while (pos < len(content) - 1):
        pos += 1
        # for debugging:
        # if (pos < begin):
        #     if content[pos] == '\n':
        #         line += 1
        #     continue
        char = content[pos]
        if content[pos] == '\n':
            line += 1
        if not (eol_comment or block_comment or single_quotes or double_quotes ):
            if content[pos:pos+2] == '//':
                eol_comment = True
            elif content[pos:pos+2] == '/*':
                block_comment = True
            elif content[pos] == '\'':
                single_quotes = True
            elif content[pos] == '\"':
                double_quotes = True
            elif search_parantheses > -1:
                if content[pos] == '(':
                    if search_parantheses == 0:
                        parantheses_start = pos
                    search_parantheses += 1
                elif content[pos] == ')':
                    if search_parantheses == 1:
                        search_parantheses = -1
                        if not (in_type == 'do'):
                            search_braces = 0
                        else:
                            do_while_found_while = True
                        parantheses_content = content[parantheses_start + 1:pos]
                    elif search_parantheses == 0:
                        print("Parantheses wrong. pos=" + pos)
                        sys.exit(1)
                    else:
                        search_parantheses -= 1
            elif search_braces > -1:
                if content[pos] == '{':
                    if (search_braces == 0) and (not in_type == 'if'):
                        # Attention! in this case two instead of one newline has to be removed!
                        insert = '\n' + get_count_line() + '\n'
                        content = content[:pos + 1] + insert + content[pos + 1:]
                        pos += len(insert)
                        line_add_count += 1
                        line += 2

                    search_braces += 1
                elif content[pos] == '}':
                    if search_braces == 1:
                        search_braces = -1
                        with_braces_found = True
                    elif search_braces == 0:
                        print("Braces wrong. pos=" + pos)
                        sys.exit(1)
                    else:
                        search_braces -= 1
                elif (search_braces == 0) and content[pos].isalpha():
                    short_without_braces = True
                    search_braces = -1
            elif short_without_braces:
                if content[pos] == ';':
                    short_without_braces_found = True
                continue
            elif short_without_braces_found or (with_braces_found and (in_type == 'if')):
                if content[pos] == '\n':
                    if in_type == 'if':
                        insert = '\n' + get_debug_line_without_count(parantheses_content, type=in_type) + '\n'
                        content = content[:if_start - 1] + insert + content[if_start - 1:]
                        pos += len(insert)
                        line_add_count += 1
                        line += 2
                    else:
                        insert = '\n' + get_debug_line_without_count(parantheses_content, type=in_type) + '\n'
                        content = content[:pos + 1] + insert + content[pos + 1:]
                        pos += len(insert)
                        line_add_count += 1
                        line += 2
                    in_type = ''
                    short_without_braces_found = False
                    with_braces_found = False
                    do_while_found_while = False
                continue
            elif with_braces_found and (in_type == 'if'):
                if content[pos] == '\n':
                    in_type = ''
                    short_without_braces_found = False
                    with_braces_found = False
                continue
            elif with_braces_found and not (in_type == 'if') and not ((in_type == 'do') and not do_while_found_while):
                if content[pos] == '\n':
                    insert = '\n' + get_debug_line(parantheses_content, type=in_type) + '\n'
                    content = content[:pos + 1] + insert + content[pos + 1:]
                    pos += len(insert)
                    line_add_count += 1
                    line += 2
                    in_type = ''
                    with_braces_found = False
                    do_while_found_while = False
                continue
            elif with_braces_found and (in_type == 'do'):
                if content[pos-len('while')+1:pos+1] == 'while':
                    search_parantheses = 0
                    with_braces_found = False
                continue

            elif content[pos-1:pos+1] == 'if' and content[pos-6:pos+1] != 'else if' and not content[pos-2].isalpha() and not content[pos+1].isalpha():
                search_parantheses = 0
                in_type = 'if'
                if_start = pos
                # Attention! in this case two instead of one newline has to be removed!
            elif content[pos-2:pos+1] == 'for' and not content[pos-3].isalpha() and not content[pos-3] == "_" and not content[pos+1].isalpha():
                search_parantheses = 0
                in_type = 'for'
                # Attention! in this case two instead of one newline has to be removed!
                insert = '\n' + get_count_init_line() + '\n'
                content = content[:pos-2] + insert + content[pos - 2:]
                pos += len(insert)
                line_add_count += 1
                line += 2
            elif content[pos-4:pos+1] == 'while' and not content[pos-5].isalpha() and not content[pos+1].isalpha():
                search_parantheses = 0
                in_type = 'while'
                # Attention! in this case two instead of one newline has to be removed!
                insert = '\n' + get_count_init_line() + '\n'
                content = content[:pos-4] + insert + content[pos - 4:]
                pos += len(insert)
                line_add_count += 1
                line += 2
            elif content[pos-1:pos+1] == 'do' and not content[pos-2].isalpha() and not content[pos+1].isalpha():
                search_braces = 0
                in_type = 'do'
                # Attention! in this case two instead of one newline has to be removed!
                insert = '\n' + get_count_init_line() + '\n'
                content = content[:pos-1] + insert + content[pos - 1:]
                pos += len(insert)
                line_add_count += 1
                line += 2


        else:
            if block_comment and (content[pos-1:pos+1] == '*/'):
                block_comment = False
            elif eol_comment and (content[pos] == '\n'):
                eol_comment = False
                pos -= 1
                line -= 1
            elif single_quotes and (content[pos] == '\''):
                single_quotes = False
            elif double_quotes and (content[pos] == '\"'):
                double_quotes = False
        # pos += 1
        # line += 1
    return content, line_add_count


def state_machine_remove():
    pass

def run_state_machine_remove(content):
    if header_comment in content:
        content = content.split(header_comment)[1]
    else:
        print("Header is missing. Probably because the CRealtimeDebug hasn\'t been added or has already been removed.")
        sys.exit(1)
    count = 0
    content_splits = []
    last_was_removed = False
    for line in content.split('\n'):
        if debug_str2 in line:
            last_was_removed = True
        else:
            if last_was_removed:
                content_splits[len(content_splits)-1] += line
                count += 1
            else:
                content_splits.append(line)
            last_was_removed = False
    content = '\n'.join(content_splits)
    return content, count

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process arguments.')
    parser.add_argument('input_file_dir', help='input file name', type=str)
    parser.add_argument('-o', '--output', help='output file name', type=str)
    parser.add_argument('-a', '--add_debug', help='Adds the debug lines', action="store_true", default=False)
    parser.add_argument('-r', '--remove_debug', help='Removes the debug lines', action="store_true", default=False)
    args = parser.parse_args()

    # Check whether the input file is correct:
    file_dir = "" + args.input_file_dir
    if os.path.isfile(file_dir):
        print("File \"" + file_dir + "\" exists.")
    else:
        print("File ", file_dir, " does not exist! Please enter a correct file.")
        sys.exit(1)

    # Read the input file:
    content = open(file_dir, 'r').read()
    original_content_length = len(content)

    # Compute
    if args.add_debug:
        content, count = run_state_machine_add(content)
        content = header_comment + content
        print(str(count) + ' debug lines have been added.')
    elif args.remove_debug:
        content, count = run_state_machine_remove(content)
        print(str(count) + ' debug lines have been removed.')

    print("\nDuring processing the length of the C++ file changed from " + str(original_content_length) + " bytes to " + str(len(content)) + " bytes.")

    # Output - either per standard output or writing to file:
    if args.output:
        output_file = open("" + args.output, "w")
        output_file.write(content)
    else:
        print("\n\n        OUTPUT:\n\n\n")
        print(content)

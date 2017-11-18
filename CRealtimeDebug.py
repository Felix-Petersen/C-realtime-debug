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

# Global var ensuring that the debug counters always have the correct name:
counter_variable_name_counter = 0

# Fixed strings:
# If "header_comment" is changed (e.g. version change) the program will remove old comment due to safety reasons.
header_comment = "/*\n" \
                 " * DEBUG by CRealtimeDebug.py     Version: 18.11.2017\n" \
                 " * All debug lines can be removed using the same script.\n" \
                 " * \n" \
                 " * CRealtimeDebug by Felix Petersen\n" \
                 " * Copyright (c) 2017 Felix Petersen. All rights reserved.\n" \
                 " */\n"
debug_str1 = "/*DEBUG by CRealtimeDebug.py*/"
debug_str2 = "/*DEBUG by CRealtimeDebug.py | Please do NOT write anything into this line*/"


# Returns the added debug line, which initializes an integer for counting the loop:
def get_count_init_line():
    global counter_variable_name_counter
    counter_variable_name_counter += 1
    return debug_str1 + "  int cRealtimeDebugInt" + str(counter_variable_name_counter) + " = 0;  " + debug_str2

# Returns the added debug line, which increases the integer that counts the loop:
def get_count_line():
    return debug_str1 + "  cRealtimeDebugInt" + str(counter_variable_name_counter) + "++;  " + debug_str2

# Returns the added debug line, which prints the result for a loop:
def get_debug_line(parantheses_content, type):
    output = debug_str1
    output += 'std::cout << "[' + args.input_file_dir + '][" << __FUNCTION__ << "][Line " << __LINE__ << "] Loop Type: ' + type
    output += ', condition: (' + parantheses_content + '), count: " << cRealtimeDebugInt' + str(counter_variable_name_counter) + ' << "\\n";  '
    output += debug_str2
    return output

# Returns the added debug line, which prints the result for an if statement (no count):
def get_debug_line_without_count(parantheses_content, type):
    output = debug_str1
    output += 'std::cout << "[' + args.input_file_dir + '][" << __FUNCTION__ << "][Line " << __LINE__ << "] Cond Type: ' + type
    output += ', condition: (' + parantheses_content + '), value: " << (' + parantheses_content + ') << "\\n";  '
    output += debug_str2
    return output

# For ensuring that there wont be an if or loop detected in a variable name etc.:
def matches_incl_whitespace(text, pattern):
    has_to_be_in = ' \n\t;(){}'
    if pattern == text[1:-1]:
        return ((text[0] in has_to_be_in) and (text[-1] in has_to_be_in))
    else:
        return False

# Adds the debug lines:
def run_add(content):
    if header_comment in content:
        print("Header is already there. Probably because the CRealtimeDebug has already been added.")
        sys.exit(1)
    pos = -1                        # current position in the document (-1 because incereased in the beginning of the loop)
    # for debugging the debugger:
    # begin = 2750
    line = 1                        # counts the lines of the document
    line_add_count = 0              # counts the added lines (in truth there are always two newlines added although only one counted)
    eol_comment = False             # current position should not be considered because its an EOL comment
    block_comment = False           # current position should not be considered because its a block comment
    single_quotes = False           # current position should not be considered because its in single quotes
    double_quotes = False           # current position should not be considered because its in double quotes
    in_type = False                 # 'if' | 'do' | 'while' | 'for'
    search_parantheses = -1         # if not -1 => pointer searches for closing parantheses
    search_braces = -1              # if not -1 => pointer searches for closing braces
    parantheses_start = 0           # saves the position of the start of the parentheses
    parantheses_content = ''        # saves the content of the last parentheses
    braces_start = 0                # saves the position of the start of the braces
    braces_content = ''             # saves the content of the last braces
    if_start = 0                    # saves the position of the start of the if statement
    short_without_braces = False    # If the if/loop is in the short syntax not requiring braces
    short_without_braces_found = False  # If the if/loop is in the short syntax not requiring braces AND the end (usually ';') has been found
    with_braces_found = False       # The end of the if/loop (usually '}') has been found
    do_while_found_while = False    # The end of the "do while" loop ('while') has been found

    # Go through the entire document:
    while (pos < len(content) - 1):
        pos += 1

        # for debugging the debugger:
        # if (pos < begin):
        #     if content[pos] == '\n':
        #         line += 1
        #     continue

        if content[pos] == '\n':
            line += 1

        # If the position should be considered:
        if not (eol_comment or block_comment or single_quotes or double_quotes ):

            # Check cases if a not considered area starts:
            if content[pos:pos+2] == '//':
                eol_comment = True
            elif content[pos:pos+2] == '/*':
                block_comment = True
            elif content[pos] == '\'':
                single_quotes = True
            elif content[pos] == '\"':
                double_quotes = True

            # If searching for closing parantheses (')') and ensuring parantheses balances:
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

            # If searching for closing braces ('}') and ensuring braces balances:
            elif search_braces > -1:
                if content[pos] == '{':
                    if search_braces == 0:
                        braces_start = pos
                    if (search_braces == 0) and (not in_type == 'if'):
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
                        # Recursively call the debug line adder on the content of the if/loop:
                        # counter_variable_name_counter is global and therefore has to be different inside the recursive call.
                        # Therefore it is saved on temp var.
                        global counter_variable_name_counter
                        temp_global_counter = counter_variable_name_counter
                        counter_variable_name_counter *= int(original_content_length / 4)
                        # Recursive call:
                        braces_content, added_lines = run_add(content[braces_start + 1:pos])
                        # Combine the new content:
                        content = content[:braces_start + 1] + braces_content + content[pos:]
                        counter_variable_name_counter = temp_global_counter
                        # Correct the position/line_add_count counters:
                        pos += len(braces_content) - len(content[braces_start + 1:pos])
                        line_add_count += added_lines
                    elif search_braces == 0:
                        print("Braces wrong. pos=" + pos)
                        sys.exit(1)
                    else:
                        search_braces -= 1
                elif (search_braces == 0) and content[pos].isalpha():
                    short_without_braces = True
                    search_braces = -1

            # If the if statement has no braces:
            elif short_without_braces:
                if content[pos] == ';':
                    short_without_braces_found = True
                continue

            # If the if/loop has no braces and the end of the statements content has been found
            # or if braces are used and found in an if statement:
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

            # If the loops (not ifs) end ('}') has been found:
            # Here it mustn't be a "do while" loop.
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

            # If the "do while" loops end (';') has been found:
            elif with_braces_found and (in_type == 'do'):
                if content[pos-len('while')+1:pos+1] == 'while':
                    search_parantheses = 0
                    with_braces_found = False
                continue

            # Checking the cases of an if/loop to begin:
            elif matches_incl_whitespace(content[pos-2:pos+2], 'if') and content[pos-6:pos+1] != 'else if':
                search_parantheses = 0
                in_type = 'if'
                if_start = pos
            elif matches_incl_whitespace(content[pos-3:pos+2], 'for'):
                search_parantheses = 0
                in_type = 'for'
                insert = '\n' + get_count_init_line() + '\n'
                content = content[:pos-2] + insert + content[pos - 2:]
                pos += len(insert)
                line_add_count += 1
                line += 2
            elif matches_incl_whitespace(content[pos-5:pos+2], 'while'):
                search_parantheses = 0
                in_type = 'while'
                insert = '\n' + get_count_init_line() + '\n'
                content = content[:pos-4] + insert + content[pos - 4:]
                pos += len(insert)
                line_add_count += 1
                line += 2
            elif matches_incl_whitespace(content[pos-2:pos+2], 'do'):
                search_braces = 0
                in_type = 'do'
                insert = '\n' + get_count_init_line() + '\n'
                content = content[:pos-1] + insert + content[pos - 1:]
                pos += len(insert)
                line_add_count += 1
                line += 2

        # If the position has not been considered because it is in a comment / String:
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

    return content, line_add_count

# Removes the debug lines:
def run_remove(content):
    # Ensure that the program has been used in the same version: (The header contains version info)
    if header_comment in content:
        content = content.split(header_comment)[1]
    else:
        print("Header is missing. Probably because the CRealtimeDebug hasn\'t been added or has already been removed.\n"
              "Possibly the used version for adding is too old.")
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
    # Parse the arguments:
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
        content, count = run_add(content)
        content = header_comment + content
        print(str(count) + ' debug lines have been added.')
    elif args.remove_debug:
        content, count = run_remove(content)
        print(str(count) + ' debug lines have been removed.')

    print("\nDuring processing the length of the C++ file changed from " + str(original_content_length) + " bytes to " + str(len(content)) + " bytes.")

    # Output - either per standard output or writing to file:
    if args.output:
        output_file = open("" + args.output, "w")
        output_file.write(content)
    else:
        print("\n\n        OUTPUT:\n\n\n")
        print(content)

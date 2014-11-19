"""
This script converts the log statements in the given file from log4j format to slf4j format.
Please see the ExampleInput.java file to see the sample input and ExampleInput.java.output
for how the converted file will look like.

For conversion purposes, the following are considered to be log statements:
    logger.trace
    logger.debug
    logger.info
    logger.error
    logger.warn
    logger.fatal
    log.trace
    log.debug
    log.info
    log.error
    log.warn
    log.fatal

The case is ignored. There can be one or more white spaces between tokens. For instance "logger   .    info" will
also be converted.

 Copyright (c) 2014 Roy <roysolvesproblems at gmail dot com>
 All rights reserved.

 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *   * Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *   * Neither the name of Redis nor the names of its contributors may be used
 *     to endorse or promote products derived from this software without
 *     specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

import os
import logging
import argparse
import re

# Customization section.
# Logger names to look for in the input Java file. If you have any other logger names in your input file,
# you should specify them here. THIS LIST IS CASE INSENSITIVE.
LOGGER_NAMES = ['logger', 'log']

# This the maximum statement length that is supported.
# This is used while replacing import statements and variable declarations.
MAX_STMT_LEN = 200

# This is the pattern for import statements.
IMPORT_STMT_RE = r'(import\s+org\s*\.\s*apache\s*\.\s*log4j\s*\..+?;)'
IMPORT_STMT_CRE = re.compile(IMPORT_STMT_RE, re.DOTALL|re.MULTILINE)

GET_LOGGER_RE = r'(Logger\s*\.\s*getLogger\s*)'
GET_LOGGER_CRE = re.compile(GET_LOGGER_RE, re.DOTALL|re.MULTILINE)
# Don't confuse this logger with the logger_name that appears in the Java program.
# This logger is for our debugging purposes.
logger = None

debug = False
input_files = []

slf4j_imports_added = False

content = None
offset = 0
logger_name = None
log_level = None

def parse_cmdline_args():
    global debug, input_files
    parser = argparse.ArgumentParser(description='Convert log4j style log statements to slf4j style statements.')
    parser.add_argument('--debug', help='Runs the program in debug mode. Writes tons of debug logs.', action='store_true')
    parser.add_argument('input_files', help='List of input files.', nargs = '+')
    args = parser.parse_args()
    debug = args.debug
    input_files = args.input_files

def setup_logging():
    global logger, debug
    # create logger
    logger = logging.getLogger('log4jtoslf4j')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    if debug: ch.setLevel(logging.DEBUG)
    else: ch.setLevel(logging.INFO)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)4.4s - %(funcName)-20s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

def clear_globals():
    """
    Clears the globals, except content and offset.
    :return:
    """
    global logger_name, log_level
    logger_name = None
    log_level = None

def read_file(file_name):
    with open(file_name) as f:
        return f.read()

def backup_file(file_name):
    logger.info("Taking a back up of [%s] with .orig extension."%file_name)
    os.rename(file_name, file_name + '.orig')

def write_file(file_name, content):
    with open(file_name, "w") as f:
        f.write(content)

def is_eof():
    global offset, content
    return offset >= len(content)

def skip_white_spaces():
    """
    Skips the white space and returns the new offset.

    :param content: Input content
    :param offset: Offset from where the whitespace should be skipped.
    :return:
    """
    global logger, content, offset
    logger.debug("Offset before: %d, len(content): %d"%(offset, len(content)))
    if offset >= len(content):
        return

    while offset < len(content) and content[offset].isspace(): offset += 1
    logger.debug("Offset after: %d"%(offset))

def capture_next_token():
    """
    Captures the next word (alpha-numeric, underscores or dot)
    :param content:
    :param offset:
    :return:
    """
    global offset
    start_pos = offset

    if is_eof(): return None

    # Dot and plus should be treated as a token in itself.
    if content[offset] in ['.', '+']:
        offset += 1
    else:
        while offset < len(content) and (content[offset].isalnum() or content[offset] == '_'):
            offset += 1

    next_token = content[start_pos:offset]
    logger.debug("Next token: %s"%next_token)
    return next_token

def looking_at_log_stmt():
    """
    Returns a tuple (<is log stmt>, <new offset>).

    :param content:
    :param offset:
    :return:
    """
    global LOGGER_NAMES, logger, offset, logger_name, log_level
    logger_name = None
    log_leval = None
    start_offset = offset

    obj_name = capture_next_token()
    logger.debug("Object name: %s"%(obj_name))
    if obj_name == None: return None

    obj_name = obj_name.strip().lower()
    if obj_name not in LOGGER_NAMES:
        offset = start_offset
        return False

    logger.debug("Captured logger: %s"%(obj_name))

    skip_white_spaces()
    dot = capture_next_token()
    logger.debug("Dot: %s"%(dot))

    if dot == None:
        offset = start_offset
        return False

    dot = dot.strip()

    if dot != '.':
        offset = start_offset
        return False

    logger.debug("Captured dot")

    skip_white_spaces()
    level = capture_next_token()
    if level == None:
        offset = start_offset
        return False

    level = level.strip()
    if level in ['trace', 'debug', 'info', 'error', 'warn', 'fatal']:
        logger_name = obj_name
        log_level = level
        return True
    else:
        offset = start_offset
        return False

def highlight_error(where):
    """
    Highlights error at a particular position. In the content.
    :param where: Offset position where the error has occurred.
    :return:
    """
    context_len = 30
    start_pos = max(where - context_len, 0)
    end_pos = min(len(content), where + context_len)
    logger.error("Error at offset: %d", where);
    if start_pos < where < end_pos:
        logger.error("%s<<%s>>%s"%(content[start_pos:where],content[where], content[where+1:end_pos]))

def move_to_matching_paren():
    global content, offset
    if content[offset] != '(':
        highlight_error(offset)
        raise Exception("Expected an open parenthesis at offset %d, but found %s"%(offset,content[offset]))
    count = 0

    while not is_eof():
        if content[offset] == '(': count += 1
        elif content[offset] == ')': count -= 1
        offset += 1

        if count == 0:
            return

def is_balanced(input):
    escape_next = False
    index = 0
    count = 0
    count_quotes = 0
    while index < len(input):
        if not escape_next:
            if input[index] in ['[', '<', '(', '{']: count += 1
            elif input[index] in [']', '>', ')', '}']: count -= 1
            elif input[index] == '"': count_quotes += 1
            escape_next = False
        else:
            if input[index] == '\\': escape_next = True

        index += 1

    return count == 0 and (count_quotes % 2) == 0

def convert_log_args():
    skip_white_spaces()
    start_offset = offset
    move_to_matching_paren()
    # Skip the opening and matching parenthesis (hence +1 and -1).
    log_args = content[start_offset + 1:offset - 1]
    log_args = log_args.strip()
    logger.debug("Log args: %s", log_args)
    log_args_split = log_args.split('+')

    # The input might already be in SLF4J format. Just skip those inputs.
    if len(log_args_split) == 1:
        return '(' + log_args + ')'

    format_string = ""
    args = ""

    for x in log_args_split:
        x = x.strip()
        if not is_balanced(x):
            logger.warn("Cannot convert log arguments: [%s] to slf4j format. Please do it maually."%log_args)
            return '(' + log_args + ')'
        if x.startswith('"'):
            x = x.strip('"')
            format_string += x
        else:
            format_string += '{}'
            if len(args) > 0:
                args += ', '
            args += x

    return '("' + format_string + '", ' + args + ')'

def looking_at_import_stmt():
    global IMPORT_STMT_CRE, content, offset
    import_key_word = 'import'
    if content.find(import_key_word, offset) != offset:
        logger.debug('Didnt find import keyword at offset %d'%offset)
        return False
    semicolon_at = content.find(';', offset)
    logger.debug('Semicolon at: %d'%semicolon_at)
    if semicolon_at == -1:
        return False
    matches = IMPORT_STMT_CRE.match(content, offset, semicolon_at + 1) is not None
    if matches:
        offset = semicolon_at + 1
        logger.debug('Is log4j import statement: %s'%matches)
    else:
        logger.debug('Import statement, but not log4j import.')
    return matches

def get_slf4j_imports_once():
    global slf4j_imports_added

    if slf4j_imports_added: return ""
    slf4j_imports_added = True
    return """
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
    """

def looking_at_get_logger_stmt():
    global GET_LOGGER_CRE, content, offset
    paren_at = content.find('(', offset)
    if paren_at == -1:
        return False
    logger.debug('Possible getLogger stmt. Checking ...')
    match = GET_LOGGER_CRE.match(content, offset, paren_at)
    matches =  match is not None
    logger.debug('Is getLogget stmt? %s'%matches)
    if matches:
        offset += len(match.group(0))
        logger.debug('Is getLogger statement? %s'%matches)
    else:
        logger.debug('Not a getLogger statement.')
    return matches


def convert(file_name):
    global content, offset, logger_name, log_level

    content = read_file(file_name)
    # print 'Content:', content

    output = ""
    index = 0
    while index < len(content):
        logger.debug("=== Index: %d"%index)
        offset = index
        logger.debug('Offset: %d'%offset)
        if looking_at_log_stmt():
            logger.debug("Looking at log stmt at offset: %d"%offset)
            logger.debug("   logger_name : %s"%logger_name)
            logger.debug("   log_level   : %s"%log_level)
            new_args = convert_log_args()
            logger.debug("   new args    : %s"%new_args)
            output += logger_name + '.' + log_level + new_args
            index = offset
        elif looking_at_import_stmt():
            output += get_slf4j_imports_once()
            index = offset
        elif looking_at_get_logger_stmt():
            output += "LoggerFactory.getLogger"
            index = offset
        else:
            output += content[index]
            index += 1
    return output

def main():
    parse_cmdline_args()
    setup_logging()
    for file_name in input_files:
        logger.info('BEGIN : Processing file: %s'%file_name)
        output = convert(file_name)
        backup_file(file_name)
        write_file(file_name, output)
        logger.info('END   : Processing file: %s'%file_name);

if __name__ == '__main__':
    main()


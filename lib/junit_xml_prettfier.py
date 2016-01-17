#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import glob
import os
import xml.etree.ElementTree

ANSI_BOLD = '\033[1m'
ANSI_RED = '\033[31m'
ANSI_GREEN = '\033[32m'
ANSI_YELLOW = '\033[33m'
ANSI_BLUE_BOLD = '\033[34;1m'
ANSI_GRAY = '\033[0;37m'
ANSI_RESET = '\033[0m'
ANSI_CLEAR = '\033[0K'
SUCCESS = '✓'
FAIL = '✗'
TESTS = 0
TIME = 0
ERRORS = 0
FAILURES = 0


def get_title(suite, tests, failures, errors, time):
  return '%s# %s: %s Tests, %s Failures, %s Errors in %ss%s' % (
      ANSI_BLUE_BOLD, suite, tests, failures, errors, time, ANSI_RESET)

def get_bold(string):
  return '%s%s%s' % (ANSI_BOLD, string, ANSI_RESET)

def get_success(title, time):
  return '  %s%s%s %s (%s)' % (
      ANSI_GREEN, SUCCESS, ANSI_RESET, title, get_time(time))

def get_error(title, time):
  return '  %s%s %s%s (%s)' % (
      ANSI_YELLOW, FAIL, title, ANSI_RESET, get_time(time))

def get_fail(title, time):
  return '  %s%s %s%s (%s)' % (
      ANSI_RED, FAIL, title, ANSI_RESET, get_time(time))

def get_time(time):
  time = float(time)
  color = ''
  if time > 0.5:
    color = ANSI_RED
  elif time > 0.1:
    color = ANSI_YELLOW
  return '%s%.3f%s seconds' % (color, time, ANSI_RESET)

def get_summary():
  color = ANSI_GREEN
  if ERRORS + FAILURES > 0:
    color = ANSI_RED
  return '%s%s     Executed %s tests, with %s errors and %s failures in' \
         ' %s seconds.%s' % (
             ANSI_BOLD, color, TESTS, ERRORS, FAILURES, TIME, ANSI_RESET)

def print_line(color):
  print '%s%s%s' % (color, ''.join(['#']*80), ANSI_RESET)

def is_travis_build():
  return os.environ.get('TRAVIS') == 'true'

def slugify(string):
  return string.lower().replace(' ', '_')

def travis_fold(name, title, body):
  if is_travis_build():
    print 'travis_fold:start:%s\r%s' % (name, ANSI_CLEAR)
  print title
  if is_travis_build():
    if body != '':
      print body
    print 'travis_fold:end:%s\r%s' % (name, ANSI_CLEAR)

def prettify_class_name(suite, class_name):
  global TESTS, ERRORS, FAILURES

  for testcase in suite.findall('testcase[@classname="%s"]' % class_name):
    children = list(testcase)
    if len(children):
      body = []
      is_error = True
      for child in children:
        if child.tag == 'error':
          body.append(ANSI_YELLOW + '    > Error:' + ANSI_RESET)
          ERRORS += 1
        elif child.tag == 'failure':
          body.append(ANSI_YELLOW + '    > Failure:' + ANSI_RESET)
          is_error = False
          FAILURES += 1
        if child.text is not None:
          body.append(child.text)
      if is_error:
        title = get_error(testcase.attrib['name'], testcase.attrib['time'])
      else:
        title = get_fail(testcase.attrib['name'], testcase.attrib['time'])
      travis_fold(slugify(class_name), title, '\n'.join(body))
    else:
      print get_success(testcase.attrib['name'], testcase.attrib['time'])
  TESTS += 1

def prettify(directory):
  global TIME

  for file_path in glob.glob('%s/*.xml' % directory):
    print ''

    suite = xml.etree.ElementTree.parse(file_path).getroot()
    print_line(ANSI_BLUE_BOLD)
    print get_title(suite.attrib['name'], suite.attrib['tests'],
                    suite.attrib['failures'], suite.attrib['errors'],
                    suite.attrib['time'])
    TIME += float(suite.attrib['time'])
    print_line(ANSI_BLUE_BOLD)

    class_names = set()
    for testcase in suite.findall('testcase'):
      class_names.add(testcase.attrib['classname'])

    for class_name in class_names:
      print ''
      if class_name != '':
        print get_bold(class_name)
      prettify_class_name(suite, class_name)

  print ''
  print get_summary()
  print ''

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'This program expects one parameter.'

  prettify(sys.argv[1])

#!/usr/bin/env python

import os
from optparse import OptionParser


class ExtensionError(Exception):
    pass


class DirectoryError(Exception):
    pass


def parse_makefile(mf):
    makefile = open(mf, 'r')
    for line in makefile:
        if 'MAIN' in line and '=' in line:
            main = line.split('=')[1].strip()
            main += '.tex'
            return main


def prepare(options, args):
    if len(args) < 1:
        parser.error('SLIDENAME required.')

    filename = args[0]

    # Split filename and extension.
    (rootname, ext) = os.path.splitext(filename)
    options.rootname = rootname

    # Check if the given SLIDENAME contains an extension. If yes, it should be
    # '.tex', otherwise something happens in a not forseen way but it can be
    # still OK, so use '--force'.
    try:
        if ext != '.tex' and '.' in filename:
            raise ExtensionError("Extension is not '.tex'! If you know what "
                                 "you are doing, use the '--force' option .")
    except ExtensionError:
        if not options.force:
            raise
        else:
            pass

    # If no extension given, set it to '.tex'
    if not ext:
        filename += '.tex'

    options.filename = filename

    filedir = options.dir
    curdir = os.getcwd()

    # There are different possibilities:
    # - If DIR has been specified, create DIR/SLIDENAME and put the .tex file
    #   there.
    # - If DIR has not been specified, check if we are in a directory called
    #   'slides':
    #   - If yes, create a directory SLIDENAME here and put the .tex file
    #     there.
    #   - If no, check if there is a directory called 'slides' in here:
    #     - If not, create one and put the .tex file there.
    if filedir:
        filedir = os.path.join(filedir, rootname)
        os.makedirs(filedir)
    elif curdir.endswith('slides'):
        os.mkdir(rootname)
        filedir = os.path.join(curdir, rootname)
    elif os.path.exists(os.path.join(curdir, 'slides')):
        filedir = os.path.join(curdir, 'slides', rootname)
        os.mkdir(filedir)
    else:
        raise DirectoryError("'slides' directory not found in current "
                             "directory. If you want another location for "
                             "your slide, please specify it with the '--dir' "
                             "option.")

    options.filedir = filedir

    if not options.title:
        options.title = rootname

    # For 'includegraphics' you need a path relative to the directory of the
    # main .tex file. This should cover most cases.
    if options.dir:
        relpath = os.path.join(os.path.basename(options.dir), rootname)
    else:
        relpath = os.path.join('slides', rootname)

    options.relpath = relpath


def make_slide(options):
    with open(os.path.join(options.filedir, options.filename), 'w') as slide:
        slide.write(
            # 'squeeze' reduces the lineskip, 'fragile' is needed if you have
            # verbatim text on the slide.
            # The 'includegraphics' are commented out as you won't need them
            # always, but it is very practical to have them here.
            '\\begin{frame}%[squeeze,fragile]\n'
            '   \\frametitle{' + options.title + '}\n'
            '   \\begin{columns}\n'
            '      \\begin{column}{.5\\textwidth}\n'
            '         %\\includegraphics[width=\\textwidth]{' +
            options.relpath + '}\n'
            '      \\end{column}\n'
            '      \\begin{column}{.5\\textwidth}\n'
            '         %\\includegraphics[width=\\textwidth]{' +
            options.relpath + '}\n'
            '      \\end{column}\n'
            '   \end{columns}\n'
            '\\end{frame}\n'
            )


# This function adds the slide to the main file of the talk.
# At this moment the slide is added before the summary slide if it is a normal
# slide and as the last slide if it is a backup slide.
def adapt_main_file(options):
    search_string = 'summary'
    spaces = ' ' * 3
    if options.backup:
        search_string = 'backupend'
        spaces = ' ' * 6

    if not options.makefile:
        options.makefile = './makefile'

    if os.path.exists(options.makefile):
        mainfile = parse_makefile(options.makefile)

        if os.path.exists(os.path.join('./', mainfile)):
            mainfile = os.path.join('./', mainfile)

            file = open(mainfile, 'r')

            # Need some acrobatics here to get the linebreaks right.
            new_file = []
            last_line = None
            for line in file:
                strip = True
                if search_string in line:
                    line_to_add = (spaces + '\\include{%s}' %
                                   os.path.join(options.relpath,
                                                options.rootname))
                    last_line += line_to_add
                    last_line = last_line.strip('\n')
                    strip = False

                    if not options.backup:
                        last_line += '\n'

                if last_line:
                    if strip:
                        last_line = last_line.strip('\n')

                    new_file.append(last_line)

                last_line = line

            new_file.append(last_line.strip('\n'))

            with open(mainfile, 'w') as main:
                for line in new_file:
                    main.write('%s\n' % line)


desc = "Create an empty slide for LaTeX Beamer."
usage = ("./%prog [options] SLIDENAME\n\n"
         "SLIDENAME is the name of the slide on the file system, i.e. it is\n"
         "the name of the subdirectory and the .tex file that will be\n"
         "generated. This subdirectory is by default created in the slides\n"
         "directory in the current directory. If you want it to be created\n"
         "eleswhere, you can use the '--dir' option.")
parser = OptionParser(usage=usage, description=desc)
parser.add_option('-d', '--dir', metavar='DIR',
                  help='Set directory where to put the slide '
                       '[default = ./slides '
                       '(if the slides directory is present)].')
parser.add_option('-t', '--title', metavar='TITLE',
                  help='Set slidetitle [default = slidename].')
parser.add_option('-f', '--force', action='store_true',
                  help="If the extension of SLIDENAME is intended to be "
                       "other than '.tex' you have to force it.")
parser.add_option('-m', '--makefile', metavar='MAKEFILE', default='./makefile',
                  help='A makefile is used to get some information. '
                       'If the default is not there, you can specify one. '
                       'Ignore this if there is no makefile '
                       '[default = %default].')
parser.add_option('-b', '--backup', action='store_true', default=False,
                  help='Set this flag when the slide is meant to be a backup '
                       'slide [default = %default].')

(options, args) = parser.parse_args()

prepare(options, args)

make_slide(options)

adapt_main_file(options)

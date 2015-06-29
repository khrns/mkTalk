#!/usr/bin/env python

import os
import shutil
import sys
from optparse import OptionParser


class ExtensionError(Exception):
    pass


class DirectoryError(Exception):
    pass


def create_makefile(talkname, talkdir):
    with open(os.path.join(talkdir, 'makefile'), 'w') as makefile:
        makefile.write(
            ".PHONY: all clean\n\n"
            "MAIN = " + talkname + "\n\n"
            "all:\n"
            "\tpdflatex ${MAIN}\n"
            "\tpdflatex ${MAIN}\n"
            "\n"
            "clean:\n"
            "\trm -f ${MAIN}.toc\n"
            "\trm -f ${MAIN}.aux\n"
            "\trm -f slides/*/*.aux\n"
            "\trm -f ${MAIN}.log\n"
            "\trm -f ${MAIN}.pdf\n"
            "\trm -f ${MAIN}.out\n"
            "\trm -f ${MAIN}.nav\n"
            "\trm -f ${MAIN}.snm\n"
            )


def prepare(options, args):
    # FIXME: BAH
    scriptname = os.path.basename(sys.argv[0])
    scriptdir = os.path.dirname(sys.argv[0])

    if len(args) < 1:
        parser.error('TALKNAME required.')

    talkname = args[0]
    filename = talkname + '.tex'

    # If the base directory for the talk is not given, use the current one.
    if options.dir is None:
        options.dir = os.getcwd()

    # FIXME: Only relative path! Make it more dynamic!!!
    if not options.preamble:
        options.preamble = 'templates/preamble.tex'

    if not options.title:
        options.title = talkname

    # If author has not been set, use the login name.
    if not options.author:
        options.author = os.getlogin()

    # Set short author.
    if not options.short_author:
        options.short_author = options.author

    talkdir = os.path.join(options.dir, talkname)

    # If the talkdir does not exists, create it.
    # If it exists don't overwrite it, abort.
    if not os.path.exists(talkdir):
        os.makedirs(talkdir)
    else:
        raise DirectoryError("Directory '%s' already exists. Please specify "
                             "a fresh directory." % talkdir)

    # FIXME: Do we need that?
    if os.path.exists(os.path.join(talkdir, scriptname)):
        parser.error("The output directory (specified with the '--dir' "
                     "option) must not contain a copy of this script!")

    # Copy some standard folders from the directory where the script is
    # located.
    dirsToCopy = [os.path.join(scriptdir, 'logo'),
                  os.path.join(scriptdir, 'slides'),
                  os.path.join(scriptdir, 'files'),
                  ]
    for dir in dirsToCopy:
        shutil.copytree(dir, os.path.join(talkdir, dir))

    shutil.copy2(os.path.join(scriptdir, 'makeSlide.py'), talkdir)

    create_makefile(talkname, talkdir)

    return talkdir, filename


def make_talk(talkpath, options):
    # options.preamble should contain everything before \\begin{document}.
    preamble = open(options.preamble, 'r').read()

    lines = []

    # Talk and author details:
    lines.append("\n\\title{%s}\n" % options.title)

    if options.subtitle:
        lines.append("\\subtitle{%s}\n" % options.subtitle)

    lines.append("\\author[%s]{\\textbf{%s}}\n" % (options.short_author,
                                                   options.author))

    if options.institute:
        lines.append("\\institute{%s}\n" % options.institute)

    lines.append("\\date{%s}\n" % options.date)

    # The actual talk:
    lines.append("\n")
    lines.append(79 * "%" + "\n")
    lines.append("% Content\n")
    lines.append(79 * "%" + "\n")
    lines.append("\n\\begin{document}\n\n")

    lines.append("   \\include{slides/title/title}\n\n")

    if not options.no_toc:
        lines.append("   \\include{slides/toc/toc}\n")

    if not options.no_outline:
        lines.append("   \\include{slides/toc/outline}\n")

    if not (options.no_toc and options.no_outline):
        lines.append("\n")

    lines.append("   \\include{slides/summary/summary}\n\n")
    lines.append("   \\include{slides/thanks/thanks}\n")

    if not options.no_backup:
        lines.append("\n")
        lines.append("   \\backupbegin\n")
        lines.append("      \\include{slides/backup/backup}\n")
        lines.append("   \\backupend\n")

    lines.append("\n\\end{document}\n")

    with open(talkpath, 'w') as talkfile:
        talkfile.write(preamble)
        for line in lines:
            talkfile.write(line)


desc = "Create a skelton for a LaTeX Beamer talk."
usage = ("./%prog [options] TALKNAME\n\n"
         "TALKNAME is a generic name of the talk that will be used for\n"
         "several purposes like the directory and/or filename of the main\n"
         ".tex file.")
parser = OptionParser(usage=usage, description=desc)
parser.add_option('-d', '--dir', metavar='DIR', default=None,
                  help='Set directory where to put the talk '
                       '[default = $PWD].')
#parser.add_option('-f', '--force', action='store_true',
                  #help="If the extension of TALKNAME is intended to be other "
                       #"than '.tex' you have to force it.")
parser.add_option('-p', '--preamble', metavar='PREAMBLEFILE',
                  help='Set (template) preamble (everything before '
                       '\\begin{document}) .tex file to use. '
                       '[default = $TALK_BASE/templates/preamble.tex]')
parser.add_option('-t', '--title', metavar='TITLE',
                  help='Set the title of the talk [default = TALKNAME].')
parser.add_option('-s', '--subtitle', metavar='SUBTITLE',
                  help='Set the subtitle of the talk [default = ].')
parser.add_option('-a', '--author', metavar='AUTHOR',
                  help='Set the author of the talk [default = $LOGIN].')
parser.add_option('-i', '--institute', metavar='INSTITUTE',
                  help='Set the institute for the talk [default = ].')
parser.add_option('--short-author', metavar='SHORTAUTHOR',
                  help='Set the short author of the talk [default = AUTHOR].')
parser.add_option('-D', '--date', metavar='DATE', default='\\today',
                  help='Set the date of the talk [default = %default].')
parser.add_option('-T', '--no-toc', action='store_true', default=False,
                  help='Suppress the table of contents slides '
                       '[default = %default].')
parser.add_option('-o', '--no-outline', action='store_true', default=False,
                  help='Suppress the outline slides [default = %default].')
parser.add_option('-b', '--no-backup', action='store_true', default=False,
                  help='Suppress the backup slides [default = %default].')

(options, args) = parser.parse_args()

talkdir, filename = prepare(options, args)

make_talk(os.path.join(talkdir, filename), options)

print "Created new talk in directory '%s'." % talkdir

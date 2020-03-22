#!/usr/bin/env python3
# Markdown Preprocessor for talks.
# Requries gpp (the generic preprocessor) to be installed.

import os
import argparse
import yaml
import _python.ndltalk as nt

parser = argparse.ArgumentParser()

parser.add_argument("filename", type=str,
                    help="Input filename")

parser.add_argument("-o", "--output", type=str,
                    help="Output filename")

parser.add_argument("--no-header", default=False, action='store_true',
                    help="Whether to search for a header in the input file (default False).")

parser.add_argument("-B", "--include-before-body", type=str,
                    help="File to include before body.")

parser.add_argument("-A", "--include-after-body", type=str,
                    help="File to include after body.")

parser.add_argument("-t", "--to", type=str,
		    choices=['pptx', 'html', 'docx', 'ipynb', 'svg', 'tex', 'python'],
                    help="Target output file format")

parser.add_argument("-w", "--whitespace", default=True, action='store_true',
                    help="Whether to remove whitespace from gpp files.")

parser.add_argument("-I", "--include-path", type=str,
                    help="include diractories")

parser.add_argument("-F", "--format", type=str,
		   choices=['notes', 'slides', 'code'],
		   help="Target output file contents")

parser.add_argument("-c", "--code", type=str, default=None,
		    choices=['none', 'sparse', 'ipynb', 'diagnostic', 'plot'],
                    help="Which parts of the code to include.")

parser.add_argument("-e", "--exercises", default=True, action='store_true',
		   help="Whether to include exercises")

parser.add_argument("-a", "--assignment", default=False, action='store_true',
		   help="Whether notes are an assignment or not")

parser.add_argument("-d", "--diagrams-dir", type=str,
                    help="Directory to find the diagrams in")


args = parser.parse_args()

diagrams_dir = '../slides/diagrams'
if args.diagrams_dir:
    diagrams_dir = args.diagrams_dir

arglist = ['+n', '-U "\\\\" "" "{" "}{" "}" "{" "}" "#" ""']
if args.to:
   arglist.append('-D{to}=1'.format(to=args.to.upper()))
if args.format:
   arglist.append('-D{format}=1'.format(format=args.format.upper()))
if args.exercises:
   arglist.append('-DEXERCISES=1')
if args.assignment:
   arglist.append('-DASSIGNMENT=1')

if args.code is not None and args.code != 'none':
   arglist.append('-DCODE=1')
   if args.code == 'ipynb':
      arglist.append('-DDISPLAYCODE=1')
      arglist.append('-DHELPERCODE=1')
      arglist.append('-DMAGICCODE=1')
   elif args.code == 'diagnostic':
      arglist.append('-DDISPLAYCODE=1')
      arglist.append('-DHELPERCODE=1')
      arglist.append('-DPLOTCODE=1')
      arglist.append('-DMAGICCODE=1')
   if args.code == 'plot':
      arglist.append('-DHELPERCODE=1')
      arglist.append('-DPLOTCODE=1')

arglist.append('-DdiagramsDir={diagrams_dir}'.format(diagrams_dir=diagrams_dir))

if args.include_path:
   arglist.append('-I{include}'.format(include=args.include_path))
if args.output:
   arglist.append('-o {}'.format(args.output))
   
filelist = []
if args.include_before_body:
   with open(args.include_before_body, 'r') as fd:
      before_text = fd.read()
else:
   before_text = ''

if args.include_after_body:
   with open(args.include_after_body, 'r') as fd:
      after_text = fd.read()
else:
   after_text = ''

if args.no_header:
   md= open(args.filename, 'r')
   body = md.read()
   md.close()
else:
   headertxt,bodytxt = nt.extract_header_body(args.filename)

header = {}
default_file = '_config.yml'
if os.path.isfile(default_file):
    md= open(default_file, 'r')
    text = md.read()
    md.close()
    header.update(yaml.load(text, Loader=yaml.FullLoader))

header.update(yaml.load(headertxt, Loader=yaml.FullLoader))
headertxt = yaml.dump(header)

if args.whitespace:
   print("Whitespace is true")


tmp_file = args.filename + 'tmp.md'
with open(tmp_file,'w') as fd:
   if not args.no_header:
      fd.write('---\n')
      fd.write(headertxt)
      fd.write('---\n')
   
   fd.write(before_text)
   fd.write(bodytxt)
   fd.write(after_text)


import os
runlist = ['gpp'] + arglist + [tmp_file]
print(' '.join(runlist))
os.system(' '.join(runlist))
#os.system('rm ' + tmp_file)
#gpp  -DPPTX=1 -DSLIDES=1 ${PPFLAGS} --include ../_includes/talk-notation.tex $< -o $output

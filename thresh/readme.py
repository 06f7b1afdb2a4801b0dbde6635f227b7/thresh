#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2016
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
help_text = """thresh (verb): to separate the wheat from the chaff.

Thresh aims to make the processing, manipulating, and analysis of
tabular data easy and fun! It allows you to get rid of what you don't
want (the chaff) and are left with what you do want (the wheat).

Examples of possible operations are: extracting columns, manipulating
columns, generating columnar data, converting file formats, and
making asserts about the data.


## Quick Start Examples

See what columns are in a file in human-readable format:

    thresh data_1.txt list

Print column names, one per line (useful for bash for-loops):

    thresh data_2.csv headerlist

Print to stdout only the columns 'time' and 'stress':

    thresh data_1.txt cat time stress

Print to stdout only the columns 'time' and 'stress' in CSV format:

    thresh data_1.txt cat time stress print .csv

Save to CSV format only the columns 'time' and 'stress':

    thresh data_1.txt cat time stress output data_out.csv

Read in from stdin (use `-.csv` for CSV format):

    cat data_1.txt | thresh - cat time stress

Print the whole file and add a millisecond column called 'mtime':

    thresh fizz_=data_1.txt cat fizz_ 'mtime=1000*time'

Print the whole file, minus column 'stress':

    thresh A=data_1.txt cat A stress=None

Make an analytic solution with columns 'time' and 'wave':

    thresh cat 'time=linspace(0,1,10)' 'wave=sin(t)'

Interpolate data:

    thresh in_=data_1.txt cat \
        'time=linspace(min(in_time),max(in_time),100)' \
        'stress=interp(time,in_time,in_stress)'

Do a simple assert on the data (return code 0 if True, 1 if False):

    thresh data_1.txt assert 'np.max(np.abs(stress)) < 2.0'

Reading in JSON and making an analytic solution:

    thresh foo.json cat "time=[0,1,2]" "stress=stress_mag * np.sin(time)"

Reading in text, CSV, and JSON for an assert:

    thresh JSON_=foo.json CSV_=bar.csv TXT_=baz.dat \
        assert "JSON_var1 + CSV_var2 + TXT_var3 == 1.23"

### Listing Column Headers

Note: you cannot `list` more than one file at a time.

See all columns in a file in a simple list.

    $ thresh column_data_1.txt headerlist
    time
    strain
    stress

See all columns in a file with extra info in human-readable format.

    thresh column_data_1.txt list
     col | length | header
    ----------------------
       0 |      4 | time
       1 |      4 | strain
       2 |      4 | stress

See the columns of the file you create.

    thresh A=data_1.txt cat A 'mtime=1000*time' list
     col | length | header
    ----------------------
       0 |      4 | time
       1 |      4 | strain
       2 |      4 | stress
       3 |      4 | mtime

Listing a JSON file just gives a pretty-printed version of the file.

    thresh data.json list
    {'magnitude': 1.23}

Loop over headers (both lines are equivalent).

    $ for COL in `thresh column_data_1.txt headerlist`; do echo Found column $COL; done
    $ thresh column_data_1.txt headerlist | while read COL; do echo Found column $COL; done
    Found column time
    Found column strain
    Found column stress

### Extracting Columns: Rules

Aliases are included to allow disambiguation of columns with the same
name in different files. For non-ambiguous column names, you can use
the aliased name or the non-aliased name.

Rules governing setting aliases:
* The alias must be a valid python identifier (variable name)
* The alias must not be a python keyword ('for', 'while', etc)
* The alias cannot conflict with a column name in any input file
* The alias cannot conflict with another alias

Some of these rules can be broken and will not cause any problems
unless you try to use an ambiguous name/alias. For example, if one
file has a column named 't' and you try to alias a file to 't', you
won't get an error unless you try to use the 't' descriptor.


### Extracting Columns with 'cat'

These are all equivalent and print all the columns.

    thresh data_1.txt
    thresh data_1.txt cat time strain stress
    thresh A=data_1.txt cat A
    thresh A=data_1.txt cat Atime Astrain Astress
    thresh A=data_1.txt cat Atime strain stress

These are equivalent (concatenate both files together with no repeated
column names).

    thresh data_1.txt data_2.txt
    thresh A=data_1.txt B=data_2.txt cat A B
    thresh A=data_1.txt B=data_2.txt cat time Astrain stress Bt eps Bsig

These are equivalent (all of one file and one column of another).
    thresh A=data_1.txt data_2.txt cat A sig
    thresh A=data_1.txt B=data_2.txt cat A sig
    thresh A=data_1.txt B=data_2.txt cat A Bsig
    thresh A=data_1.txt B=data_2.txt cat Atime Astrain Astress Bsig
    thresh A=data_1.txt data_2.txt cat Atime strain stress sig


### Manipulating Columns
create a new file with a single column called 'mtime' which is
milliseconds (all equivalent).

    thresh data_1.txt cat mtime=1000*time
    thresh A=data_1.txt cat mtime=1000*time
    thresh A=data_1.txt cat mtime=1000*Atime

Create a new column based on data from a file and then use that
new column to create another column.

    thresh data_1.txt cat \
      'dstress=np.diff(stress)' \
      'dt=np.diff(time)' \
      'stress_rate=dstress / dt'


### Creating New Files With No Input File

Create a new file that with numbers and their squares.
    thresh cat 't=arange(1,6,1)' 'squares=t**2'
       t  squares
       1        1
       2        4
       3        9
       4       16
       5       25

Create a new file that has a sine wave and a noisy sine wave.
    thresh cat \
      't=linspace(0.0,pi,100)' \
      'sine=sin(t)' \
      'noisey=sine+random.uniform(-1.0,1.0,len(sine))'


### Performing an Assert

In some instances, you will want to make checks/asserts on the data and
get feedback in the form of a return code (like for automated tests).
One or more assert statements can be made and compound statements are
okay. The returned value is cast to a boolean and the program terminates
with a return code of 0 if it evaluates to True and 1 if it evaluates to
False.

Do a simple assert on the data.

    thresh data_1.txt assert "abs(max(a)-6.0) < 1.0e-6"

Do a less simple assert

    thresh data_1.txt \
        cat 'stress_rate=np.diff(stress)/np.diff(time)' \
        assert 'np.max(np.abs(stress_rate)) < 2.0'

Use multiple asserts (all asserts must pass for 0 return code).

    thresh data_1.txt \
        cat 'stress_rate=np.diff(stress)/np.diff(time)' \
        assert \
            'np.max(np.abs(stress_rate)) < 2.0' \
            'np.all(strain >= 0)'

Use a compound statement.

    thresh data_1.txt \
        cat 'stress_rate=np.diff(stress)/np.diff(time)' \
        assert 'np.max(np.abs(stress_rate)) < 2.0 or np.all(strain >= 0)'


### Saving output

Several different output formats are supported.

Regular whitespace-delimited otuput to stdout:

    thresh data_1.txt print

CSV output to stdout

    thresh data_1.txt print .csv

Regular whitespace-delimited otuput to foo.txt

    thresh data_1.txt output foo.txt

CSV output to foo.csv

    thresh data_1.txt output foo.csv

### Manipulating columns with special characters

Some column names will have special characters that would make the
column name invalid in python syntax. The work-around requires that the
file in question is aliased. The column is accessed in this manner:

```bash
$ thresh A=data.txt cat "good_name=__aliases['A']['-bad_name%']" assert "max(good_name) > 1"
```

Notes:
* While columns with special names may be accessed this way, they
  cannot be assigned in this way.
* This is only available in the 'cat' section and not in the 'assert'
  section. If you wish to access a "bad" column for assert, give it
  a "good" name in the 'cat' section and use that name in the assert
  section.
"""

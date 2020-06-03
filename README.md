# thresh

The _thresh_ module is meant primarily as a python module for a command-line tool for manipulating files containing data in columns.

Examples of possible operations are: extracting a single column from a file, merging two files with columns, shifting or scaling a column.


## Quick Start Examples

```bash
# Read in a file and write it out in whitespace-delimited format.
# Using '-' as a filename instructs thresh to read from stdin.
$ thresh data_1.txt
$ cat data_1.txt | thresh -
```

```bash
# See what columns are in a file.
$ thresh data_1.txt list
```

```bash
# Alias the file to A and print the whole file.
$ thresh A=data_1.txt cat A

# Cat only the columns 'time' and 'stress'.
# (output column headers are 'time' and 'stress' even when aliased)
$ thresh data_1.txt cat time stress
$ thresh A=data_1.txt cat Atime Astress

# Cat the whole file, plus a millisecond column 'mtime'
$ thresh A=data_1.txt cat A 'mtime=1000*time'

# Cat the whole file, minus column 'stress'
$ thresh A=data_1.txt cat A stress=None
```

```bash
# Make an analytic solution with columns 'time' and 'wave'.
$ thresh cat 'time=linspace(0,1,10)' 'wave=sin(t)'
```

```bash
# Interpolate data.
$ thresh data_1.txt \
  cat 'time1=linspace(min(time),max(time),100)' 'stress1=interp(time1,time,stress)'
```

```bash
# Do a simple check on the data (return code 0 if True, 1 if False).
$ thresh data_1.txt \
  cat 'stress_rate=np.diff(stress)/np.diff(time)' \
  check 'np.max(np.abs(stress_rate)) < 2.0'
```


### Listing Column Headers

```bash
# See all columns in a file.
$ thresh column_data_1.txt list
 col | length | header
----------------------
   0 |      4 | time
   1 |      4 | strain
   2 |      4 | stress
```

```bash
# See the columns of the file you create.
$ thresh A=data_1.txt cat A 'mtime=1000*time' list
 col | length | header
----------------------
   0 |      4 | time
   1 |      4 | strain
   2 |      4 | stress
   3 |      4 | mtime
```

Note: you cannot `list` more than one file at a time.


### Extracting Columns: Rules

Aliases are included to allow disambiguation of columns with the same
name in different files. For non-ambiguous column names, you can use
the aliased name or the non-aliased name.

Rules governing setting aliases:
* The alias must be one character followed by an equal sign '='.
* The alias must be a letter (a-zA-Z)
* The alias cannot conflict with a column name in any input file
* The alias cannot conflict with another alias

Some of these rules can be broken and will not cause any problems
unless you try to use an ambiguous name/alias. For example, if one
file has a column named 't' and you try to alias a file to 't', you
won't get an error unless you try to use the 't' descriptor.


### Extracting Columns

```bash
# These are all equivalent and print all the columns.
$ thresh data_1.txt
$ thresh data_1.txt cat time strain stress
$ thresh A=data_1.txt cat A
$ thresh A=data_1.txt cat Atime Astrain Astress
$ thresh A=data_1.txt cat Atime strain stress

# These are equivalent (concatenate both files together with no repeated
# column names).
$ thresh data_1.txt data_2.txt
$ thresh A=data_1.txt B=data_2.txt cat A B
$ thresh A=data_1.txt B=data_2.txt cat time Astrain stress Bt eps Bsig

# These are equivalent (all of one file and one column of another).
$ thresh A=data_1.txt data_2.txt cat A sig
$ thresh A=data_1.txt B=data_2.txt cat A sig
$ thresh A=data_1.txt B=data_2.txt cat A Bsig
$ thresh A=data_1.txt B=data_2.txt cat Atime Astrain Astress Bsig
$ thresh A=data_1.txt data_2.txt cat Atime strain stress sig
```


### Manipulating Columns
```bash
# create a new file with a single column called 'mtime' which is
# milliseconds (all equivalent)
$ thresh data_1.txt cat mtime=1000*time
$ thresh A=data_1.txt cat mtime=1000*time
$ thresh A=data_1.txt cat mtime=1000*Atime

# Create a new column based on data from a file and then use that
# new column to create another column.
$ thresh data_1.txt cat \
  'dstress=np.diff(stress)' \
  'dt=np.diff(time)' \
  'stress_rate=dstress / dt'
```


### Creating New Files With No Input File
```bash
# Create a new file that with numbers and their squares
$ thresh cat 't=arange(1,6,1)' 'squares=t**2'
   t  squares
   1        1
   2        4
   3        9
   4       16
   5       25
```

```bash
# Create a new file that has a sine wave and a noisey sine wave
$ thresh cat \
  't=linspace(0.0,pi,100)' \
  'sine=sin(t)' \
  'noisey=sine+random.uniform(-1.0,1.0,len(sine))'
```

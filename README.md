# thresh

The _thresh_ module is meant primarily as a python module for a command-line tool for manipulating files containing data in columns.

Examples of possible operations are: extracting a single column from a file, merging two files with columns, shifting or scaling a column.


## Quick Start Examples

```bash
# Read in a file and write it out in whitespace-delimited format.
# using '-' as a filename instructs thresh to read from stdin.
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
# (column headers are 'time' and 'stress' even when aliased)
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
$ thresh column_data_1.txt list
==> column_data_1.txt <==
 idx    name    alias    length
   1    time                  5
   2  strain                  5
   3  stress                  5
```

```bash
$ thresh A=column_data_1.txt list
==> column_data_1.txt <==
 idx    name    alias    length
   1    time    Atime          5
   2  strain  Astrain          5
   3  stress  Astress          5
```



```bash
$ thresh column_data_1.txt column_data_2.txt list
==> column_data_1.txt <==
  1 time
  2 strain
  3 stress

==> column_data_2.txt <==
  1 time
  2 density
  3 pressure
```

## Wish List

### Extracting Columns: Rules

Rules governing setting aliases:
* The alias must be one character followed by an equal sign '='.
* The alias must be a letter (a-zA-Z)
* The alias cannot conflict with a column name in any input file
* The alias cannot conflict with another alias

Rules for determining the column for extracting (all matches must be
exact and unique):
* If column descriptor exactly matches one alias, interpret as if all
  columns in the file were given. There cannot be two matches because
  two files with the same alias is not allowed.
* If the column descriptor exactly matches one column header, insert
  column. If more than one match, it's an error.
* Check for valid alias+name "Acolname" at start of descriptor. If valid
  interpret as that column.

### Extracting Columns

```bash
# These are equivalent
$ thresh data_1.txt cat time strain stress
$ thresh data_1.txt cat
$ thresh A=data_1.txt cat
$ thresh A=data_1.txt cat A
$ thresh A=data_1.txt cat Atime Astrain Astress
$ thresh A=data_1.txt cat Atime strain stress

# These are equivalent
$ thresh data_1.txt data_2.txt cat
$ thresh A=data_1.txt B=data_2.txt cat
$ thresh A=data_1.txt B=data_2.txt cat A B

# These are equivalent
$ thresh A=data_1.txt data_2.txt cat A density
$ thresh A=data_1.txt B=data_2.txt cat A density
$ thresh A=data_1.txt B=data_2.txt cat A Bdensity
$ thresh A=data_1.txt B=data_2.txt cat Atime Astrain Astress Bdensity
$ thresh A=data_1.txt data_2.txt cat Atime strain stress density
```

### Manipulating Columns
```bash
# create a new column called 'mtime' which is milliseconds (all equivalent)
$ thresh data_1.txt cat mtime=1000*time
$ thresh A=data_1.txt cat mtime=1000*time
$ thresh A=data_1.txt cat mtime=1000*Atime
```

### Creating new files
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
$ thresh cat 't=linspace(0.0,pi,100)' 'sine=sin(t)' 'noisey=sine+random.uniform(-1.0,1.0,len(sine))'
```



### Splitting Files into Many Single-Column Files

```bash
$ thresh column_data_1.txt burst
Created column_data_1_time.txt
Created column_data_1_strain.txt
Created column_data_1_stress.txt
```

```bash
$ thresh column_data_1.txt column_data_2.txt burst
Created column_data_1_time.txt
Created column_data_1_strain.txt
Created column_data_1_stress.txt
Created column_data_2_time.txt
Created column_data_2_density.txt
Created column_data_2_pressure.txt
```

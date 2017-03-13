# thresh

The _thresh_ module is meant primarily as a python module for a command-line tool for manipulating files containing data in columns.

Examples of possible operations are: extracting a single column from a file, merging two files with columns, shifting or scaling a column.


## Usage Examples

The most basic functionality for _thresh_ is listing column headers and splitting files, as stated above.

### Listing Column Headers

```bash
$ thresh column_data_1.txt list
==> column_data_1.txt <==
  1 time
  2 strain
  3 stress
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
$ thresh data_1.txt cat time=1000*time
$ thresh data_1.txt cat time=1000*Atime
$ thresh data_1.txt cat Atime=1000*time
$ thresh A=data_1.txt cat Atime=1000*Atime
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

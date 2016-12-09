# thresh

The _thresh_ module is meant primarily as a python module for a command-line tool for manipulating files containing data in columns.


## Usage Examples

The most basic functionality for _thresh_ is listing column headers and splitting files.

### Listing Column Headers

```bash
$ thresh column_data_1.txt list
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

### Splitting Files into Many Single-Column Files

```bash
$ thresh column_data_1.txt burst
Created time.txt
Created strain.txt
Created stress.txt
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

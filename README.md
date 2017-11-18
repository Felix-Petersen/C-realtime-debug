# C++-realtime-debug
Print evaluated booleans which are used in conditions (if, for, while...) for debug purposes.

Counts the number of repeats in loops.

## Example

Here is an example for the use of the program at an if condition:

```c++
if (ii % 1000 == 0) {
    std::cout << "*";
}
```

=>

```c++
/*DEBUG by CRealtimeDebug.py*/std::cout << "[main.cpp][" << __FUNCTION__ << "][Line " << __LINE__ << "] Cond Type: if, condition: (i % 1000 == 0), value: " << (i % 1000 == 0) << "\n";  /*DEBUG by CRealtimeDebug.py | Please do NOT write anything into this line*/
if (ii % 1000 == 0) {
    std::cout << "*";
}
```

Outputs in console:

```
[main.cpp][update_screen][Line 434] Cond Type: if, condition: (i % 1000 == 0), value: 0
```
```
[main.cpp][update_screen][Line 434] Cond Type: if, condition: (i % 1000 == 0), value: 1
```

## Usage

### Example

For adding the debug lines use `./CRealtimeDebug.py -a -o main_debug.cpp main.cpp` and for removing them `./CRealtimeDebug.py -r -o main_not_debug.cpp main_debug.cpp`.Please save your files before using this program.

### Shell help

```
usage: CRealtimeDebug.py [-h] [-o OUTPUT] [-a] [-r] input_file_dir

Process arguments.

positional arguments:
  input_file_dir        input file name

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file name
  -a, --add_debug       Adds the debug lines
  -r, --remove_debug    Removes the debug lines
```

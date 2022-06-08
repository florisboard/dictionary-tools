**This repository is deprecated beginning with FlorisBoard 0.4.0-alpha01 and is superseded by [florisboard/nlp](https://github.com/florisboard/nlp)! For the purpose of creating AOSP dictionares the scripts provided by this repo can still be used, however it will not be usable within FlorisBoard.**

---

# dictionary-tools
Repository which hosts the tool(s) required to build a binary dictionary file
from raw source set(s). Used for providing dictionary assets to FlorisBoard.

This repository is based on https://github.com/remi0s/aosp-dictionary-tools,
which is licensed under the terms of the Apache 2.0 license. The following
components are taken from the original repository:

- Dictionary builder jar file (`dicttool_aosp.jar`), unmodified
- The syntax for the AOSP dicttool jar arguments
- The format for how a combined-list must look like to be able to be compiled
  into a binary dictionary

Some parts of `clb.py` are based on https://github.com/LuminosoInsight/wordfreq,
which provides an explaination on how to work with `cBpack` source files for
creating word lists. The frequency calculation itself has been completely
changed so it works together with the format needed for the dictionary file.

## Prerequisites
In order to use this tool, you need the following tools installed on your
machine:
- Python 3 (Tested with 3.8.5, but other 3.X versions should all be compatible)
- The pip module `msgpack` (To work with the file format of the `cBpack` files)
- Java(TM) SE Runtime Environment 1.8.0 or higher when building AOSP Dictionary
  files. Not required when making [Flictionaries](flictionary.md).

This tool has been tested on Windows 10 as well as on Linux Mint, but it should
also run fine on other Linux distros, as long as the above prerequisites are
installed.

## Usage
`./dicttool.py <command> [<arguments>]`

Available commands:
- `clean`       Cleans up the .dicttool folder in this directory.
- `help`        Shows a help dialog.
- `make`        Makes a single dictionary with these required arguments:<br>
                 `<lang_code> <src_type> <src_path> <dst_type>`
- `makeall`     Makes all dictionares defined in the static list `makeall.py`.

Currently supported `<src_type>` values:
- `cBpack`: Centibel-pack style sources. See https://github.com/LuminosoInsight/wordfreq
  for more information and examples.

Currently supported `<dst_type>` values:
- `flict`: Creates a Flictionary
- `dict`: Creates an AOSP Dictionary with the help of `dicttool_aosp.jar`

The output is within the `.dicttool` sub-directory, which will automatically be
created if it does not exist.

## Other notes
This repository only provides the tools for creating binary `.dict`/`.flict`
files from various source formats. The actual source files have to be provided
by yourself.

~The main purpose for this repository is to provide a useful tool for creating
dictionaries which will be used in [FlorisBoard].~
Of course, this can also be used to create dictionary files for other
open-source keyboards as well, as long as the dictionary format needed is also
the binary output format (`.dict`).

## License
For binary dictionaries created with this tool, the license terms of your used
source apply, this tool does not add any additional terms.

The source code of this tool is licensed under the following terms:

```
Copyright 2021 Patrick Goldinger

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

[FlorisBoard]: https://github.com/florisboard/florisboard

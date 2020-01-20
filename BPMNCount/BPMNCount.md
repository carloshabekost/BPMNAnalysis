This module counts elements in a set of .bpmn files in a single, one-level folder (meaning it does not consider files in child folders).

It has dependencies on pandas, bs4, lxml and PySimpleGUI. Pandas is used to store intermediate informations and deliver the output file; 
bs4 and lxml allow us to navigate the .bpmn files; 
and PySimpleGUI is used to provide a more user-friendly interface with which to work with the module.

Some of those packages have their own requirements, as follows:

- pandas requires numpy, pytz and python-dateutil.
- bs4 requires beautifulsoup4, which requires soupsieve.
- PySimpleGUI requires tkinter.

The module allows as an input parameter an empty list of files, but must have an output location specified. This is by design.

WARNING: This module overwrites any file with the same name as the output.

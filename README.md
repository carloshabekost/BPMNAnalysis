# BPM-Pesquisa
Work developed with the BPM-INF-UFRGS research group.

1. [BPMNCount](https://github.com/Berger-DM/BPM-Pesquisa/tree/master/BPMNCount) - BPMN Element counting in .bpmn files, distinguishing their variations and subprocess presence.

    This module counts elements in a set of .bpmn files in a single, one-level folder (meaning it does not consider files in child folders).

    It has dependencies on pandas, bs4, lxml and PySimpleGUI. Pandas is used to store intermediate information and deliver the output file in .csv format; 
    bs4 and lxml allow us to navigate the .bpmn files efficiently and with legible code; 
    and PySimpleGUI is used to provide a more user-friendly interface with which to work with the module, again with legible code.

    Some of those packages have their own requirements, as follows:

    - pandas requires numpy, pytz and python-dateutil.
    - bs4 requires beautifulsoup4, which requires soupsieve.
    - PySimpleGUI requires tkinter.

    The module allows as an input parameter an empty list of files, but must have an output location specified. This is by design.

    WARNING: This module overwrites any file with the same name as the output.

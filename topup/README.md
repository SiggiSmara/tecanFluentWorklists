# Topup

Here the goal was to increase the volume in one aliquot to a user defined value. The aliquots were 
in a 96 well plate format with source and destination plates containing the source for the top
up liquid and the destination that should contain the desired volume.

Added complications were that although the source and the destination contained the same samples
they were not in the same position within the 96 well plate. So each sample had to have an
id that correlates between the source and the desination.

Also in some cases the aliquot in the destination surpassed or equalled the wanted final
volume in which case nothing was to happen (no removal of liquid in the destination).

And a sample tracking list was to be produced keeping track of source and destination 
and how much volume was added.


## Files and file structure

### convert2gwl.py

The main workhorse that generates the worklist. It reads the volumes from a file whose
path is given as a run time parameter. The name of the file also indicates the source 
and destination plate barcodes. In the barcodes folder each plate has it's own excel
file that contains the information needed (location, barcode of the aliquot and id of
the sample). The script read both of them and makes sure that all sample ids are accounted 
for. Then it read the detected volumes of the destination and calculates how much is needed
for each sample. And finally it writes the corresponding worklist in a separate directory,
called worklists.

### finalizeRun.py

Here is where the sample tracking list was generated. It relies on having sample tracking enabled
on the Fluent as it read the exported data from the Fluent and made it into a unified list,
combining also the barcodes of the individual tubes. 

### toBuildEXE.txt

Explains briefly how the .exe file was generated as python was not installed on the computer
that ran the Fluent control software.
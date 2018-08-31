# Multisplit

Here we were splitting one large source tube into several smaller aliquots. The wanted outcome was that 
each smaller aliquot would be of a user setable value with the last aliquot containing the remaining volume
of the source. Added complexity was that the minimum and maximum of the final aliquot had to be within
certain limits as well.

Other features were that a sample tracking list was to be produced keeping track of the
location and the volume of each aliquot and from which source it came.

## Files and file structure

### convert2gwl.py

The main workhorse that generates the worklist. It reads the volumes from the files listed in convertParams.txt
and based on that information makes the necessary splits. Here it was needed to have two reads of the
source as it was quite full and the final dispenses were inaccurately estimating the volume left.
This is also reflected in the one or two lines found in the convertParams.txt file indicating if
this was the first or the second read.

### convertParams.txt

See convert2gwl.py above

### finalizeRun.py

Here is where the sample tracking list was generated. It relies on having sample tracking enabled
on the Fluent as it read the exported data from the Fluent and made it into a unified list,
combining also the barcodes of the individual tubes. The final step is to save all of the
generated files along the sources to a new directory.

### toBuildEXE.txt

Explains briefly how the .exe file was generated as python was not installed on the computer
that ran the Fluent control software.
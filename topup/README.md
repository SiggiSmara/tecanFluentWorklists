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

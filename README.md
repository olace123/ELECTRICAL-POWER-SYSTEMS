# ELECTRICAL-POWER-SYSTEMS
this contains functions for power systems analysis 

some comments in the code are currently in Spanish but the essentials are in English.

The sep module must be in the same folder as the Gauss seidel for it to work correctly.
The 2 text files must also be in the same folder, they are the files that the program uses to work.
In the bus_data file: write in lowercase letters in the node type column if it is: "slack", "pq" or "pv"; depending on the type is the code that processes it.
For the slack node in the column of pg (real power generated) and qg (reactive power generated), you can put any number, it only has to be an integer or floating, it is only so that the space is not blank, the same for the pv node in the column of qd (reactive power demanded).

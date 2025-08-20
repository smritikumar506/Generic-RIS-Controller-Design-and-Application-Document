The codes attached and the design documents corespond to Generic RIS Controller, where RIS beamforming can be controlled in field deployments by Generic RIS Controller,through a pre-calberated Lookup table, when the Channel Estimation logic exposes the recived signal strength to GRC. GRC's decision on Beamforming angle is communicated to RIS controller, via RIS specific controller Logic (RSC).
We also provide the code to calibrate the Look Up table.
Operation Sequence for LUT Calibration.... CE.py -> LUT.py
Operation Sequence for RIS Control CE.py -> RSC.py -> GRC.py
We have provided python codes for GNU radio simple cosine tone Transmission and reception vis USRP B200.
Every module is replacable by User's own logic if only the system to expose data between codes is used as it is or can be replaced by other python ipcs like socket. FIFO  etc.

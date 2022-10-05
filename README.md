# NBISFingerprintScanner
Biometric Fingerprint Scanner written in python and hosted on a raspberry pi 4.
---------------------------------------
This is skeleton code for a more complex system. GUI is verry primitive and is handled in a terminal window, the database is handled locally, and encryption is less than adequate for a real biometric system. Also the NBIS software is subpar in my opinion, this was just a fun project to make a functional fingerprint scanner. Included is the automation script written in python, the NBIS modules needed, the database files for the print templates, and the 3d model of the housing for the project. Listed below are the harware components, and softwares and python modules I used.
---------------------------------------
Harware Compenents:
Raspberry Pi 4
ArduCam pi camera v1
Prism
Infared Light
---------------------------------------
Dependancies:
NIST BIometric Imaging Software
Python Modules:
 OS 
 Time
 Picamera
 Subprocess
 sqlite3
 fernet

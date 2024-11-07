@echo off

:: windows only i guess
:: has to be run in radio_scripts folder
:: set max_freqs=433430 433500 433570
:: Define an array of max_freq values
set min_freq=433200
set max_freqs=433210 
set trans_port="COM7"
set receive_port="COM5"

:: Loop through each max_freq value
for %%f in (%max_freqs%) do (
    :: Open new terminal for set_radio_parameters.py with custom title and wait until it finishes
    start /wait "set_radio_parameters" cmd /c python "set_radio_parameters.py" %trans_port% %receive_port% %min_freq% %%f 

    timeout /t 3

    :: wysylanie z jakiegos powodu odblokowywuje odbiornik? wychodzi z command mode'a?
    start "dziury_send" cmd /c python "dziury_send.py" %receive_port%
    timeout /t 4
    taskkill /FI "IMAGENAME eq python3.12.exe" /F

    start "dziury_send" cmd /c python "dziury_send.py" %trans_port% 

    :: Open new terminal for dziury_receive.py with custom title and wait until it finishes
    start /wait "dziury_receive" cmd /c python "dziury_receive.py" %receive_port% %min_freq% %%f

    :: Wait for processes to finish before killing them
    timeout /t 2

    :: Kill the terminal windows 
    taskkill /FI "IMAGENAME eq python3.12.exe" /F
)
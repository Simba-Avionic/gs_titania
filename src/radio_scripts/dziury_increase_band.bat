@echo off

:: Define variables
set min_freq=433200
set max_freqs=433910
set trans_port="COM7"
set receive_port="COM5"
set reading_period=7
set sending_frequencies=500
set air_speeds=64 

:: Loop through each max_freq value
for %%f in (%max_freqs%) do (
    for %%x in (%sending_frequencies%) do (
        for %%y in (%air_speeds%) do (

            :: Set radio parameters
            start /wait "set_radio_parameters" cmd /c python "set_radio_parameters.py" %trans_port% %receive_port% %min_freq% %%f %air_speeds%
            timeout /t 3

            :: Send message on receive port
            start "dziury_send" cmd /c python "dziury_send.py" %receive_port% %%x
            timeout /t 4
            taskkill /FI "IMAGENAME eq python3.12.exe" /F

            :: Send message on transmit port
            start "dziury_send" cmd /c python "dziury_send.py" %trans_port% %%x
            
            :: Start receiving
            start /wait "dziury_receive" cmd /c python "dziury_receive.py" %receive_port% %min_freq% %%f %reading_period% %%x %%y

            :: Wait and terminate Python processes
            timeout /t 2
            taskkill /FI "IMAGENAME eq python3.12.exe" /F
        )
    )
)
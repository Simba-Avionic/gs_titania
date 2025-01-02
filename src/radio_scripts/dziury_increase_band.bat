@echo off

:: Define variables
set min_freq=433100
set max_freqs=433300 440000 
set trans_port="COM5"
set receive_port="COM8"
set reading_period=7
set sending_frequencies=100 110 120 130
set air_speeds=192 
set baud_rate=57600
set power=20
:: Loop through each max_freq value
for %%f in (%max_freqs%) do (
    for %%y in (%air_speeds%) do (
        :: Set radio parameters
        start /min /wait "set_radio_parameters" cmd /c python "set_radio_parameters.py" %trans_port% %receive_port% %baud_rate% %min_freq% %%f %%y %power%
        timeout /t 1
        for %%x in (%sending_frequencies%) do (
            :: Send message on receive port
            start /min "dziury_send" cmd /c python "dziury_send.py" %receive_port% %%x
            timeout /t 2
            taskkill /FI "IMAGENAME eq python.exe" /F
            timeout /t 1

            :: Send message on transmit port
            start /min "dziury_send" cmd /c python "dziury_send.py" %trans_port% %%x
            
            :: Start receiving
            start /min /wait "dziury_receive" cmd /k python "dziury_receive.py" %receive_port% %min_freq% %%f %reading_period% %%x %%y

            :: Wait and terminate Python processes
            timeout /t 2
            taskkill /FI "IMAGENAME eq python.exe" /F
        )
    )
)
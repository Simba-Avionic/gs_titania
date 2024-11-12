@echo off

:: windows only i guess
:: has to be run in mavlink_examples folder
:: both radios has to be connected to the same pc
set sending_frequencies=200 300 400

for %%f in (%sending_frequencies%) do (

    start  "test_send" cmd /c python "test_send.py" %%f
    start /wait "test_receive" cmd /c python "test_receive.py"

)

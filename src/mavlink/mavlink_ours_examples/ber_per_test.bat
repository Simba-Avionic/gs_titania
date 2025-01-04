@echo off

:: windows only i guess
:: has to be run in mavlink_examples folder
:: both radios has to be connected to the same pc

start "ber_per_test_receive" cmd /c python "ber_per_test_receive.py"

start "ber_per_test_send" cmd /c python "ber_per_test_send.py"



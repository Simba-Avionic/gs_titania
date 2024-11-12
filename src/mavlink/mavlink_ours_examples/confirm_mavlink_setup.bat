@echo off

:: windows only i guess
:: has to be run in mavlink_examples folder
:: both radios has to be connected to the same pc

start "confirm_mavlink_setup_receive" cmd /c python "confirm_mavlink_setup_receive.py"

start "confirm_mavlink_setup_send" cmd /c python "confirm_mavlink_setup_send.py"



@echo off

:: windows only i guess
:: has to be run in tests folder
:: both radios has to be connected to the same pc

set trans_port="COM7"
set receive_port="COM5"
set baud_rate=57600

start "ultimate_test_receive" cmd /k python "ultimate_test_receive.py" %receive_port% %baud_rate%

start "ultimate_test_send" cmd /k python "ultimate_test_send.py" %trans_port% %baud_rate%



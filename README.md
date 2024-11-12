# gs_titania
Ground Segment - radio 433

## Setup
0. Create python virtual environment `python3 -m venv venv`
1. Install required packages `pip install -r requirements.txt`

## To create and compile custom mavlink dialects (assumes setup was done), this is for python on windows (might be wiser if needed to implement custom messages in C)
1. Move to the top of the gs_titania repo
2. Copy message definitions to venv `cp -r venv\Lib\site-packages\pymavlink\message_definitions\v1.0 venv\Lib\site-packages\message_definitions\v1.0`
3. Create custom dialect .xml file with custom messages 
4. To use custom dilect you need to specify it name while connecting to module
```
from pymavlink import mavutil
mavlink_sender = mavutil.mavlink_connection('COM7', baud=57600,dialect='custom_dialect')
```
5. if you want to recompile the custom dialect you need to delete both the .py and .xml files of your dialect in `gs_titania\venv\Lib\site-packages\pymavlink\dialects\v10\`
`rm venv\Lib\site-packages\pymavlink\dialects\v10\custom_dialect.*`

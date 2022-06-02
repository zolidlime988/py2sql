# Py2SQL.py

This Program will execute and run an automation work on Linux Server to provide the database updating and prepare for the Arduino to read it from the database.

# GetData.php

This PHP script will execute every period of time(I and my team have decided to set the trigger of 2 seconds). It will Get the data from arduino and runs the SQL query by the get value from farm.

# smartfarm.php

This PHP script will execute with the GetData.php. It will Get the data from SQL and send back to arduino.

# Webapp(ReactJS)

Noted that users can adjust the automation process via WebApp. You can view for more detail at https://github.com/Jaytitaya?tab=repositories

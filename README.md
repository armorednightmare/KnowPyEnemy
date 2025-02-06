# KnowPyEnemy
KnowPyEnemy - Python based extension processing ArcDps logs to show information about enemy numbers

## Requirements

- Windows 10/11
- Install Python 3.12 or compatible version
- Install required packages mentioned in requirement.txt, e.g. with `pip install -r requirements.txt`

## Usage

### Setup
- Download repository
- run Setup.py
  - set the path to your ARCDPS logs when asked
    - usually this is `%USERPROFILE%\Documents\Guild Wars 2\addons\arcdps\arcdps.cbtlogs`
 
### Service/Observer
While playing in WvW, this will show you the details just after each encouter. 
Keep in mind, processing large log files might take a while to complete. 

- run python KnowPyEnemy_service.py

### Script processing
In the case you forgot to run the service and still want to know the details for the last few encounters:

- run KnowPyEnemy.py 

## Example
![image](https://github.com/user-attachments/assets/2214b665-86b6-4140-95ef-33b0f4580187)

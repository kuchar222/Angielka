from datetime import datetime, timedelta
import time

data1 = datetime.now()
time.sleep(4)
data2 = datetime.now()

if data2 - data1 > timedelta(seconds=5):
    print('OK')
else:
    print('Nie')

print(data2-data1)
# print(data1)
# print(data2)
from datetime import datetime
from time import sleep

now = datetime.now()

sleep(67)

diff = datetime.now() - now

print(diff.total_seconds() / 60)




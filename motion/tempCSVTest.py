from time import sleep

from tempLogCSV import TempCSV

temp = TempCSV()

# temp.write(20,45, 52)

t = 5

while True:
    print(temp.get_temp_c())
    sleep(1)
    t +=1
    temp.write(t, 45, 52)

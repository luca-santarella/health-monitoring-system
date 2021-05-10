#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import sleep
import time, math
import asyncio
import aioschedule as schedule
import time
import requests

WRITE_API_KEY = ""
max_speed = 0

dist_meas = 0.00
km_per_hour = 0
rpm = 0
elapse = 0
sensor = 15
pulse = 0
THING_TWEET_KEY = ""
start_timer = time.time()

async def send_data():
	global max_speed, pulse, dist_meas
	print("sending data")
	r = requests.get("https://api.thingspeak.com/update?api_key="+WRITE_API_KEY+"&field5="+str(round(dist_meas,1))+"&field6="+str(round(max_speed,1))+"&field7="+str(pulse))

async def reset_data():
	global max_speed, pulse, dist_meas, rpm, km_per_hour
	max_speed = 0
	pulse = 0
	dist_meas = 0
	rpm=0
	km_per_hour = 0

async def tweet_data():
	global max_speed, pulse, dist_meas
	print("tweeting data")
	status = "Today I ran "+str(round(dist_meas,1))+" meters and I have completed "+str(pulse)+" loops in my wheel."
	resp = requests.post("https://api.thingspeak.com/apps/thingtweet/1/statuses/update", data={"api_key":THING_TWEET_KEY, "status":status})
    

def init_GPIO():					# initialize GPIO
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(sensor,GPIO.IN,GPIO.PUD_UP)

def calculate_elapse(channel):				# callback function
	global pulse, start_timer, elapse
	pulse+=1								# increase pulse by 1 whenever interrupt occurred
	elapse = time.time() - start_timer		# elapse for every 1 complete rotation made!
	start_timer = time.time()				# let current time equals to start_timer

def calculate_speed(r_cm):
	global pulse,elapse,rpm,dist_km,dist_meas,km_per_sec,km_per_hour, max_speed
	if elapse !=0:							# to avoid DivisionByZero error
		rpm = 1/elapse * 60
		circ_cm = (2*math.pi)*r_cm			# calculate wheel circumference in CM
		dist_km = circ_cm/100000 			# convert cm to km
		km_per_sec = dist_km / elapse		# calculate KM/sec
		km_per_hour = km_per_sec * 3600		# calculate KM/h
		dist_meas = (dist_km*pulse)*1000	# measure distance traverse in meter
		if(km_per_hour>max_speed):
			max_speed = km_per_hour
		return km_per_hour

def init_interrupt():
	GPIO.add_event_detect(sensor, GPIO.FALLING, callback = calculate_elapse, bouncetime = 200)

if __name__ == '__main__':
	init_GPIO()
	init_interrupt()
	schedule.every().day.at("08:00").do(tweet_data)
	schedule.every(3600).seconds.do(send_data)
	schedule.every().day.at("08:05").do(reset_data)
	loop = asyncio.get_event_loop()
	while True:
		loop.run_until_complete(schedule.run_pending())
		calculate_speed(7)	# call this function with wheel radius as parameter
		print('rpm:{0:.0f}-RPM kmh:{1:.0f}-KMH dist_meas:{2:.2f}m pulse:{3}'.format(rpm,km_per_hour,dist_meas,pulse))
		sleep(0.1)

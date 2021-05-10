#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO
from TCS34725 import TCS34725
import requests
import ctypes

active = 0
trigger_pin = 16
channel_id = ""
WRITE_API_KEY = ""
THING_TWEET_KEY = ""

class SHTC3:
	def __init__(self):
		self.dll = ctypes.CDLL("./SHTC3.so")
		init = self.dll.init
		init.restype = ctypes.c_int
		init.argtypes = [ctypes.c_void_p]
		init(None)

	def SHTC3_Read_Temperature(self):
		temperature = self.dll.SHTC3_Read_TH
		temperature.restype = ctypes.c_float
		temperature.argtypes = [ctypes.c_void_p]
		return temperature(None)
	def SHTC3_Read_Humidity(self):
		humidity = self.dll.SHTC3_Read_RH
		humidity.restype = ctypes.c_float
		humidity.argtypes = [ctypes.c_void_p]
		return humidity(None)

def set_active(pin):
	active = 1

def tweet_alert(status):
	resp = requests.post("https://api.thingspeak.com/apps/thingtweet/1/statuses/update", data={"api_key":THING_TWEET_KEY, "status":status})

def main():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(trigger_pin,GPIO.IN)
	HumTemp=SHTC3()
	Light=TCS34725(0X29, debug=False)
	if(Light.TCS34725_init() == 1):
		print("TCS34725 initialization error!!")
	else:
		print("TCS34725 initialization success!!")

	time.sleep(2)
	try:
		active = 0
		GPIO.add_event_detect(trigger_pin, GPIO.RISING, callback=set_active)
		while True:
			active = GPIO.input(trigger_pin)
			Light.Get_RGBData()
			lux = round(Light.Get_Lux(),1)
			if(lux > 100):
				tweet_alert("WARNING, there is too much light!! Bit's cage is "+str(lux)+" lux")
			temp = round(HumTemp.SHTC3_Read_Temperature(),1)
			if temp < 22:
				tweet_alert("WARNING, temperature too low!! Bit's cage is "+str(temp)+"°")
			if temp > 28:
				tweet_alert("WARNING, temperature too high!! Bit's cage is "+str(temp)+"°")
			hum = round(HumTemp.SHTC3_Read_Humidity(),1)
			if hum > 50:
				tweet_alert("WARNING, humidity too high!! Bit's cage is "+str(hum)+"%")
			r = requests.get("https://api.thingspeak.com/update?api_key="+WRITE_API_KEY+"&field1="+str(lux)+"&field2="+str(temp)+"&field3="+str(hum)+"&field4="+str(active))
			time.sleep(60)
            
	except Exception as ex:
		print(ex)
		time.sleep(5)
		pass


if __name__ == "__main__":
    
	main()
    


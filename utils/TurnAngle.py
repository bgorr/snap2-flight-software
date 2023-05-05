import Jetson.GPIO as GPIO
import time

channel = 31

GPIO.setmode(GPIO.BOARD)


i = 0

def callback_fn(channel):
	global i
	global start_time
	global desired_angle
	global motor1
	i += 1

	time2 = time.perf_counter()
	run_time = start_time - time2
	freq = i / run_time
	motor_freq = freq / 16
	RPM = motor_freq * 60
	RPM = RPM / 150
	deg_s = RPM * 6
	total_deg = deg_s * run_time
	print(total_deg)
	if abs(total_deg) >= desired_angle:
		motor1.stop()

def run_motor_1(angle, power=20):
	global i
	global desired_angle
	desired_angle = angle
	i = 0
	output_pin = 33
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
	global motor1
	motor1 = GPIO.PWM(output_pin, 18000)
	duty_cycle = power

	channel = 31
	
	
	GPIO.setup(channel, GPIO.IN)
	GPIO.add_event_detect(channel, GPIO.RISING, callback=callback_fn)
	
	global start_time
	start_time = time.perf_counter()
	motor1.start(duty_cycle)
	

	del i
	del motor1
	del desired_angle
	del start_time
	i = 0


import time
import Jetson.GPIO as GPIO
import datetime
import os
import io
import numpy as np
import IMU
import sys

# setup all pins
motor_pin_alt = 33
motor_pin_az = 32
encoder_alt_pin = 21
encoder_az_pin = 7
rev_pin = 23
faults_pin = 26
en_pin = 29
# setup all pins to be used
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor_pin_alt, GPIO.OUT)
GPIO.setup(encoder_alt_pin, GPIO.IN)
GPIO.setup(motor_pin_az,GPIO.OUT)
GPIO.setup(encoder_az_pin,GPIO.IN)
GPIO.setup(rev_pin,GPIO.OUT)
GPIO.setup(faults_pin,GPIO.IN)
GPIO.setup(en_pin,GPIO.OUT)
# Set up PWM output
motor_alt_pwm = GPIO.PWM(motor_pin_alt, 1000)  # 1000 Hz PWM frequency
motor_az_pwm = GPIO.PWM(motor_pin_az, 1000)
# Set up PID parameters & variables
Kp = 0.5
Ki = 0.1
Kd = 0.2

# encoder
pulses_per_rev = 20838 # need to change this idk if calculated with wrong gearing ratio or what
angle_per_pulse = 360 / pulses_per_rev

def reverse_motors(reverse_pin):
    """reverses the direction of both motor"""
    # Check the current state of the pin
    pin_state = GPIO.input(reverse_pin)
    # Swap the output
    if pin_state == 0:
        GPIO.output(reverse_pin, GPIO.HIGH)
    elif pin_state == 1:
        GPIO.output(reverse_pin, GPIO.LOW)
    else:
        "screwed up"

def enable_driver(enable_pin):
    GPIO.output(enable_pin, GPIO.HIGH)

def disable_driver(enable_pin):
    GPIO.output(enable_pin, GPIO.LOW)

def driver_fault_detect(fault_pin):
    pin_state = GPIO.input(fault_pin)
    if pin_state == 1:
        print("Fault detected either over current or over temperature")

def setup_fault_detection(fault_pin):
    """sets up the fault detection for the motor driver"""
    # Set the pin numbering mode
    GPIO.setmode(GPIO.BOARD)

    # Set the pin as an input pin
    GPIO.setup(fault_pin, GPIO.IN)

    # Add event detection for the rising edge (GPIO.LOW to GPIO.HIGH)
    GPIO.add_event_detect(fault_pin, GPIO.RISING, callback=driver_fault_detect)

def get_current_angles():
    with open('altitude_angle_encoder_tel.txt','rb') as data:
        try:
            data.seek(-2, os.SEEK_END)
            while data.read(1)!= b'\n':
                data.seek(-2, os.SEEK_CUR)
        except OSError:
            data.seek(0)
        telem = data.readline().decode()
    telem = telem.split(',')
    altitude_angle=float(telem[0])
    with open('azimuth_angle_encoder_tel.txt','rb') as data:
        try:
            data.seek(-2, os.SEEK_END)
            while data.read(1)!= b'\n':
                data.seek(-2, os.SEEK_CUR)
        except OSError:
            data.seek(0)
        telem = data.readline().decode()
    telem = telem.split(',')
    azimuth_angle=float(telem[0])
    return(altitude_angle,azimuth_angle)

# initialize altitude and azimuth angles
altitude_angle,azimuth_angle = get_current_angles()

def encoder_count_alt(channel):
    global altitude_angle
    pin_state = GPIO.input(rev_pin)
    if pin_state == 0:
        altitude_angle += angle_per_pulse
    else:
        altitude_angle -= angle_per_pulse


def encoder_count_az(channel):
    global azimuth_angle
    pin_state = GPIO.input(rev_pin)
    if pin_state == 0:
        azimuth_angle += angle_per_pulse
    else:
        azimuth_angle -= angle_per_pulse

GPIO.add_event_detect(encoder_alt_pin, GPIO.RISING, callback=encoder_count_alt)
GPIO.add_event_detect(encoder_az_pin, GPIO.RISING, callback=encoder_count_az)

# altidue motor
def run_motor_alt(target_alt_angle):
# check if desired motion is in bounds
#    if abs(target_alt_angle) > 45:
#        print("Target Angle Out of Bounds: Altitude angle must be in (-45,45) degrees")
#        return 
    
    motor_alt_pwm.start(0)  

    rev_pin_state = GPIO.input(rev_pin)
    if target_alt_angle < altitude_angle and rev_pin_state == 0:
        reverse_motors(rev_pin)
    elif target_alt_angle > altitude_angle and rev_pin_state == 1:
        reverse_motors(rev_pin)
    error_sum = 0
    last_error = 0
    last_time = time.time()
    # Loop until target angle is reached will stop when within 0.05 degree
    while abs(altitude_angle - target_alt_angle) > .5:
        # Calculate error and error_sum
        error = target_alt_angle - altitude_angle
        error_sum += error

        # Calculate delta_time and last_error
        delta_time = time.time() - last_time
        last_time = time.time()
        delta_error = error - last_error
        last_error = error

        # Calculate PID output
        output = Kp * error + Ki * error_sum * delta_time + Kd * delta_error / delta_time
        output = 20
        # Apply PID output to motor
        duty_cycle = max(min(output, 100), 0)  # Limit duty cycle to 0-100%
        motor_alt_pwm.ChangeDutyCycle(duty_cycle)

        # Wait for next loop iteration
        time.sleep(0.01)  # 100 Hz loop frequency

    # Stop the motor
    motor_alt_pwm.ChangeDutyCycle(0)
    motor_alt_pwm.stop()
    time.sleep(0.4)
    with open('altitude_angle_encoder_tel.txt','a') as data:
        data.write(str(altitude_angle) + ',' + str(datetime.datetime.now()) + '\n')

# azimuth motor
def run_motor_az(target_az_angle):
# check if desired motion is in bounds
    if abs(target_az_angle) > 45:
        print("Target Angle Out of Bounds: Altitude angle must be in (-45,45) degrees")
        return None
    
    motor_az_pwm.start(0)

    rev_pin_state = GPIO.input(rev_pin)
    if target_az_angle < azimuth_angle and rev_pin_state == 0:
        reverse_motors(rev_pin)
    elif target_az_angle > azimuth_angle and rev_pin_state == 1:
        reverse_motors(rev_pin)


    error_sum = 0
    last_error = 0
    last_time = time.time()
    # Loop until target angle is reached will stop when within 0.05 degree
    while abs(azimuth_angle - target_az_angle) > 0.5:
        # Calculate error and error_sum
        error = target_az_angle - azimuth_angle
        error_sum += error

        # Calculate delta_time and last_error
        delta_time = time.time() - last_time
        last_time = time.time()
        delta_error = error - last_error
        last_error = error

        # Calculate PID output
        output = Kp * error + Ki * error_sum * delta_time + Kd * delta_error / delta_time
        output = 20
        # Apply PID output to motor
        duty_cycle = max(min(output, 100), 0)  # Limit duty cycle to 0-100%
        motor_az_pwm.ChangeDutyCycle(duty_cycle)

        # Wait for next loop iteration
        time.sleep(0.01)  # 100 Hz loop frequency

    # Stop the motor
    motor_az_pwm.ChangeDutyCycle(0)
    motor_az_pwm.stop()
    time.sleep(.4) # wait one second to allow motor to stop
    with open("azimuth_angle_encoder_tel.txt",'a') as data:
        data.write(str(azimuth_angle) + ',' + str(datetime.datetime.now()) + '\n')


def print_current_angles():
    print("Current Altitude Angle:",altitude_angle)
    print("Current Azimuth Angle:",azimuth_angle)

def scan_pattern():
    alt_min = -20
    alt_max = 20
    az_min = -20
    az_max = 20
    step_size = 2
    az_angles = np.arange(-20,20,step_size)
    alt_angles = np.arange(-20,20,step_size)
    for az_angle in az_angles:
        run_motor_az(az_angle)
        print(az_angle,'az')
        for alt_angle in alt_angles:
            print(alt_angle)
            run_motor_alt(alt_angle)
            time.sleep(1)  # Pause foraltitude_angle 1 second to capture images

        # Reverse the direction of altitude movement for the next azimuth level
        alt_angles = -1 * alt_angles
    
    # Return gimbal to the neutral position
    run_motor_alt(0)
    run_motor_az(0)


def plume_tracking():
# slew to plume position
    while True:
        rel_plume_alt, rel_plume_az = get_plume_angles() #assuming this exists
# calculate absolute angle of plume
        abs_plume_alt = altitude_angle + rel_plume_alt
        abs_plume_az = azimuth_angle + rel_plume_az
# slew to plume
        run_motor_alt(abs_plume_alt)
        run_motor_az(abs_plume_az)

        time.sleep(1)

def zero_alt_angle_imu():
    global altitude_angle

    imu_angles = IMU.IMU()
    roll = imu_angles.get_ypr()[2]
    abs_angle = altitude_angle - roll
    run_motor_alt(abs_angle)
    time.sleep(1)

    with open('altitude_angle_encoder_tel.txt','a') as data:
        data.write(str(0) + ',' + str(datetime.datetime.now()) + '\n')

    altitude_angle = 0

# test of the gimbal control
enable_driver(en_pin)
try:
# first test manual control
    run_motor_az(float(sys.argv[1]))
    run_motor_alt(float(sys.argv[2]))
        


#    time.sleep(1)
#    run_motor_alt(0)
#    time.sleep(1)
#    run_motor_az(10)
#    time.sleep(1)
#    run_motor_az(0)
#    print("about to test automatic scan pattern")
#    time.sleep(5)
#    scan_pattern()

except Exception as e:
    motor_alt_pwm.stop()
    motor_az_pwm.stop()
    print(e)
    GPIO.cleanup()
finally:
    motor_alt_pwm.stop()
    motor_az_pwm.stop()
    GPIO.cleanup()
    


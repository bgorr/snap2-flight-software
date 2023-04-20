import time
import Jetson.GPIO as GPIO
import datetime
import os
import io
import numpy as np
import IMU

class GimbalControl():
    def __init__(self):
        # setup all pins
        self.motor_pin_alt = 33
        self.motor_pin_az = 32
        self.encoder_alt_pin = 21
        self.encoder_az_pin = 7
        self.rev_pin = 23
        self.faults_pin = 26
        self.en_pin = 29
        # setup all pins to be used
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.motor_pin_alt, GPIO.OUT)
        GPIO.setup(self.encoder_alt_pin, GPIO.IN)
        GPIO.setup(self.motor_pin_az,GPIO.OUT)
        GPIO.setup(self.encoder_az_pin,GPIO.IN)
        GPIO.setup(self.rev_pin,GPIO.OUT)
        GPIO.setup(self.faults_pin,GPIO.IN)
        GPIO.setup(self.en_pin,GPIO.OUT)
        # Set up PWM output
        self.motor_alt_pwm = GPIO.PWM(self.motor_pin_alt, 1000)  # 1000 Hz PWM frequency
        self.motor_az_pwm = GPIO.PWM(self.motor_pin_az, 1000)
        # Set up PID parameters & variables
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.2

        # encoder
        self.pulses_per_rev = 20838 # need to change this idk if calculated with wrong gearing ratio or what
        self.angle_per_pulse = 360 / self.pulses_per_rev

        # initialize altitude and azimuth angles
        self.altitude_angle,self.azimuth_angle = self.get_current_angles()
        self.rev_pin_state = GPIO.input(self.rev_pin)
        GPIO.add_event_detect(self.encoder_alt_pin, GPIO.RISING, callback=self.encoder_count_alt)
        GPIO.add_event_detect(self.encoder_az_pin, GPIO.RISING, callback=self.encoder_count_az)

    def reverse_motors(self):
        """reverses the direction of both motor"""
        # Swap the output
        if self.rev_pin_state == 0:
            self.rev_pin_state = 1
            GPIO.output(self.rev_pin, GPIO.HIGH)
        elif self.rev_pin_state == 1:
            self.rev_pin_state = 0
            GPIO.output(self.rev_pin, GPIO.LOW)
        else:
            "screwed up"

    def enable_driver(self):
        GPIO.output(self.en_pin, GPIO.HIGH)

    def disable_driver(self):
        GPIO.output(self.en_pin, GPIO.LOW)

    def driver_fault_detect(self):
        pin_state = GPIO.input(self.fault_pin)
        if pin_state == 1:
            print("Fault detected either over current or over temperature")

    def setup_fault_detection(self):
        """sets up the fault detection for the motor driver"""
        # Set the pin numbering mode
        GPIO.setmode(GPIO.BOARD)

        # Set the pin as an input pin
        GPIO.setup(self.fault_pin, GPIO.IN)

        # Add event detection for the rising edge (GPIO.LOW to GPIO.HIGH)
        GPIO.add_event_detect(self.fault_pin, GPIO.RISING, callback=driver_fault_detect)

    def get_current_angles(self):
        with open('altitude_angle_encoder_tel.txt','rb') as data:
            try:
                data.seek(-2, os.SEEK_END)
                while data.read(1)!= b'\n':
                    data.seek(-2, os.SEEK_CUR)
            except OSError:
                data.seek(0)
            telem = data.readline().decode()
        telem = telem.split(',')
        self.altitude_angle=float(telem[0])
        with open('azimuth_angle_encoder_tel.txt','rb') as data:
            try:
                data.seek(-2, os.SEEK_END)
                while data.read(1)!= b'\n':
                    data.seek(-2, os.SEEK_CUR)
            except OSError:
                data.seek(0)
            telem = data.readline().decode()
        telem = telem.split(',')
        self.azimuth_angle=float(telem[0])
        return(self.altitude_angle,self.azimuth_angle)

    def encoder_count_alt(self,channel):
        if self.rev_pin_state == 0:
            self.altitude_angle += self.angle_per_pulse
        else:
            self.altitude_angle -= self.angle_per_pulse


    def encoder_count_az(self,channel):
        if self.rev_pin_state == 0:
            self.azimuth_angle += self.angle_per_pulse
        else:
            self.azimuth_angle -= self.angle_per_pulse

    # altidue motor
    def run_motor_alt(self,target_alt_angle):
    # check if desired motion is in bounds
    #    if abs(target_alt_angle) > 45:
    #        print("Target Angle Out of Bounds: Altitude angle must be in (-45,45) degrees")
    #        return 
        
        self.motor_alt_pwm.start(0)  

        
        error_sum = 0
        last_error = 0
        last_time = time.time()
        # Loop until target angle is reached will stop when within 0.05 degree
        while abs(self.altitude_angle - target_alt_angle) > .05:
            if target_alt_angle < self.altitude_angle and self.rev_pin_state == 0:
                self.reverse_motors()
            elif target_alt_angle > self.altitude_angle and self.rev_pin_state == 1:
                self.reverse_motors()
            # Calculate error and error_sum
            error = target_alt_angle - self.altitude_angle
            error_sum += error

            # Calculate delta_time and last_error
            delta_time = time.time() - last_time
            last_time = time.time()
            delta_error = error - last_error
            last_error = error

            # Calculate PID output
            output = self.Kp * error + self.Ki * error_sum * delta_time + self.Kd * delta_error / delta_time
            output = 10
            # Apply PID output to motor
            duty_cycle = max(min(output, 100), 0)  # Limit duty cycle to 0-100%
            self.motor_alt_pwm.ChangeDutyCycle(duty_cycle)

            # Wait for next loop iteration
            time.sleep(0.01)  # 100 Hz loop frequency

        # Stop the motor
        self.motor_alt_pwm.ChangeDutyCycle(0)
        self.motor_alt_pwm.stop()
        time.sleep(0.4)
        with open('altitude_angle_encoder_tel.txt','a') as data:
            data.write(str(self.altitude_angle) + ',' + str(datetime.datetime.now()) + '\n')

    # azimuth motor
    def run_motor_az(self,target_az_angle):
    # check if desired motion is in bounds
        if abs(target_az_angle) > 45:
            print("Target Angle Out of Bounds: Altitude angle must be in (-45,45) degrees")
            return None
        
        self.motor_az_pwm.start(0)




        error_sum = 0
        last_error = 0
        last_time = time.time()
        # Loop until target angle is reached will stop when within 0.05 degree
        while abs(self.azimuth_angle - target_az_angle) > 0.05:
            if target_az_angle < self.azimuth_angle and self.rev_pin_state == 0:
                self.reverse_motors()
            elif target_az_angle > self.azimuth_angle and self.rev_pin_state == 1:
                self.reverse_motors()
            # Calculate error and error_sum
            error = target_az_angle - self.azimuth_angle
            error_sum += error

            # Calculate delta_time and last_error
            delta_time = time.time() - last_time
            last_time = time.time()
            delta_error = error - last_error
            last_error = error

            # Calculate PID output
            output = self.Kp * error + self.Ki * error_sum * delta_time + self.Kd * delta_error / delta_time
            output = 10
            # Apply PID output to motor
            duty_cycle = max(min(output, 100), 0)  # Limit duty cycle to 0-100%
            self.motor_az_pwm.ChangeDutyCycle(duty_cycle)

            # Wait for next loop iteration
            time.sleep(0.01)  # 100 Hz loop frequency

        # Stop the motor
        self.motor_az_pwm.ChangeDutyCycle(0)
        self.motor_az_pwm.stop()
        time.sleep(.4) # wait one second to allow motor to stop
        with open("azimuth_angle_encoder_tel.txt",'a') as data:
            data.write(str(self.azimuth_angle) + ',' + str(datetime.datetime.now()) + '\n')


    def print_current_angles(self):
        print("Current Altitude Angle:",self.altitude_angle)
        print("Current Azimuth Angle:",self.azimuth_angle)

    def scan_pattern(self,controller):
        alt_min = -20
        alt_max = 20
        az_min = -20
        az_max = 20
        step_size = 2
        az_angles = np.arange(-20,20,step_size)
        alt_angles = np.arange(-20,20,step_size)
        for az_angle in az_angles:
            self.run_motor_az(az_angle)
            print(az_angle,'az')
            for alt_angle in alt_angles:
                controller.data_capture(self.get_current_angles())
                if(controller.plume_state == True):
                    self.track_plume(controller)
                else:
                    print(alt_angle)
                    self.run_motor_alt(alt_angle)
                #time.sleep(1)  # Pause for 1 second to capture images TODO remove?
            # Reverse the direction of altitude movement for the next azimuth level
            alt_angles = -1 * alt_angles
        
        # Return gimbal to the neutral position
        self.run_motor_alt(0)
        self.run_motor_az(0)
        return

    def track_plume(self,controller):
        if controller.plume_state is True:
            angles = self.centroid_to_degrees(controller.plume_pos)
            target_x = angles[0] # x corresponds to alt bc of camera orientation
            target_y = angles[1] # y corresponds to az
            self.run_motor_alt(self.altitude_angle+target_x)
            self.run_motor_az(self.azimuth_angle+target_y)
            return
        else:
            print("Done tracking plume!")
            return

    def centroid_to_degrees(self,loc_tuple):
        alt = (loc_tuple[0] - 256.0) * 0.0167
        az = (loc_tuple[1] - 256.0) * 0.0167
        return (alt,az)
# if __name__ == "__main__":
#     try:
#         gc = GimbalControl()
#         gc.enable_driver()
#         gc.scan_pattern()
#     except Exception as e:
#         gc.motor_alt_pwm.stop()
#         gc.motor_az_pwm.stop()
#         print(e)
#         e.printStackTrace()
#         GPIO.cleanup()
#     finally:
#         gc.motor_alt_pwm.stop()
#         gc.motor_az_pwm.stop()
#         GPIO.cleanup()
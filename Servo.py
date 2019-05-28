from flask import Flask, render_template_string,render_template, request, redirect, url_for, make_response# Importing the Flask modules required for this project
import RPi.GPIO as GPIO     # Importing the GPIO library to control GPIO pins of Raspberry Pi
from time import sleep      # Import sleep module from time library to add delays
import socket
# Pins where we have connected servos
servo_pin =   27        
servo_pin1 = 22
 
GPIO.setmode(GPIO.BCM)      # We are using the BCM pin numbering
# Declaring Servo Pins as output pins
GPIO.setup(servo_pin, GPIO.OUT)     
GPIO.setup(servo_pin1, GPIO.OUT)
 
# Created PWM channels at 50Hz frequency
p = GPIO.PWM(servo_pin, 50)
p1 = GPIO.PWM(servo_pin1, 50)
 
# Initial duty cycle
p.start(0)
p1.start(0)
 
# Flask constructor takes the name of current module (__name__) as argument.
app = Flask(__name__)
# Enable debug mode
app.config['DEBUG'] = True
 
# Store HTML code
TPL = '''
<html>
    <head><title>Web Application to control Servos </title></head>
    <body>
    <h2> Web Application to Control Servos</h2>
        <form method="POST" action="test">
            <p>Slider 1 <input type="range" min="0" max="180" name="slider1" /> </p>
            <p>Slider 2 <input type="range" min="0" max="180" name="slider2" /> </p>
            <input type="submit" value="submit" />
        </form>
    </body>
</html>
'''
# Get server ip
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
server_ip = s.getsockname()[0]
s.close()
# which URL should call the associated function.
@app.route("/")
def home():
    return render_template_string(TPL)
    return render_template(server_ip=server_ip)
    
 
@app.route("/test", methods=["POST"])
def test():
    # Get slider Values
    slider1 = request.form["slider1"]
    slider2 = request.form["slider2"]
    DC =  1./18*float(slider1) + 2
    DC1 = 1./18*float(slider2) + 2
    # Change duty cycle
    p.ChangeDutyCycle(DC)
    p1.ChangeDutyCycle(DC1)
    sleep (0.1)
    #p1.ChangeDutyCycle(float(slider2))
    # Give servo some time to move
    #sleep(1)
    # Pause the servo
    p.ChangeDutyCycle(0)
    p1.ChangeDutyCycle(0)
    return render_template_string(TPL)
app.run(debug=True, host='0.0.0.0', port=8000) 
 
# Run the app on the local development server
#if __name__ == "__main__":
#    app.run()


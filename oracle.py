#activate_this = 'home/oracle/oracle/myenv/bin/activate_this.py'
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))
import sys
sys.path.append('/home/oracle/oracle/myenv/lib/python3.9/site-packages')
import openai

import RPi.GPIO as GPIO
import time
import os
import subprocess
from datetime import datetime
from RPLCD import CharLCD

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Keypad configuration
KEYPAD = [
    ['1', '2', '3', 'F'],
    ['4', '5', '6', 'E'],
    ['7', '8', '9', 'D'],
    ['A', '0', 'B', 'C']
]

# GPIO setup
ROW_PINS = [19, 21, 8, 10]
COL_PINS = [36, 38, 22, 32]

# External device control GPIO setup
RIGHT = 5
A = 7
DOWN = 16
UP = 18
B = 11
LEFT = 12
SELECT = 13
START = 15

control_pins = [RIGHT, LEFT, DOWN, UP, B, A, SELECT, START]

# Set GPIO mode to BOARD
wait_button = 40

# Setup input and output pins
for pin in ROW_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for pin in COL_PINS + control_pins:
    GPIO.setup(pin, GPIO.OUT)

# Setup wait button separately
GPIO.setup(wait_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
 
# Initialize the LCD
lcd = CharLCD(
    numbering_mode=GPIO.BOARD,
    cols=16,
    rows=2,
    pin_rs=37,
    pin_rw=None,
    pin_e=35,
    pins_data=[33, 31, 29, 23]
)

# Define a dictionary to map keys to pins
KEY_TO_PIN = {
    '2': UP,
    '4': LEFT,
    '5': DOWN,
    '6': RIGHT,
    'C': A,
    'B': B,
    'A': SELECT,
    '0': START
}

# LCD update for mode change
def lcd_update_mode():
    lcd.clear()
    mode_message = 'Control Mode ON' if control_mode else 'Control Mode OFF'
    lcd.write_string(mode_message)
    time.sleep(1)  # Let the message be on for 1 second
    lcd.clear()
    lcd.write_string(u'Insert offering\n\ror press ENTER')

def check_keypad():
    key = None
    press_time = 0
    for j in range(len(COL_PINS)):
        GPIO.output(COL_PINS[j], 0)
        for i in range(len(ROW_PINS)):
            if GPIO.input(ROW_PINS[i]) == 0:
                key = KEYPAD[i][j]
                print(f"Key Press Detected: {key}")  # Print statement for key press
                press_time_start = time.time()
                time.sleep(0.2)  # Debounce delay
                while GPIO.input(ROW_PINS[i]) == 0:
                    pass
                press_time = time.time() - press_time_start
                if key == "F" and press_time >= 3:
                    global control_mode
                    control_mode = not control_mode
                    lcd_update_mode()
                break
        GPIO.output(COL_PINS[j], 1)
        if key:
            break
    return key, press_time

# Add a control mode flag
control_mode = False

# Define control functions
def pulse_enable():
    GPIO.output(lcd.pin_e, GPIO.HIGH)
    time.sleep(0.0005)
    GPIO.output(lcd.pin_e, GPIO.LOW)
    time.sleep(0.0005)

# Pulse timing for "pressing" Game Boy buttons. Still tweaking this. 
def pulse_pin(pin):
    if pin == START:
        GPIO.output(pin, 1)
        time.sleep(0.3)
        GPIO.output(pin, 0)
        time.sleep(4)
    elif pin == RIGHT:
        GPIO.output(pin, 1)
        time.sleep(0.3)
        GPIO.output(pin, 0)
        time.sleep(0.7)
    else:
        GPIO.output(pin, 1)
        time.sleep(0.3)
        GPIO.output(pin, 0)
        time.sleep(0.7)

def get_birthdate():
    lcd.clear()
    lcd.write_string(u'Enter your\n\rbirthdate(MMDD):')

    birthdate = ""
    while True:
        key, press_time = check_keypad()

        if key:
            if key == "C":
                break
            elif key == "A":  # Backspace functionality
                birthdate = birthdate[:-1]
                lcd.clear()
                if len(birthdate) == 0:
                    lcd.write_string(u'Enter your\n\rbirthdate(MMDD):')
                else:
                    lcd.write_string(birthdate + "\n\rthen ENTER ---->")
            elif key == "F" and press_time >= 2:
                global control_mode
                control_mode = not control_mode  # Toggle control mode
                if control_mode:
                    lcd.clear()
                    lcd.write_string(u'Control Mode ON')
                else:
                    lcd.clear()
                    lcd.write_string(u'Control Mode OFF')
            elif not control_mode and key.isdigit():  # Only add to birthdate if not in control mode and key is a digit
                valid_input = False
                # Validate input based on position in birthdate
                if len(birthdate) == 0 and key in ["0", "1"]:
                    birthdate += key
                    valid_input = True
                elif len(birthdate) == 1:
                    if birthdate[0] == "0" or (birthdate[0] == "1" and key in ["0", "1", "2"]):
                        birthdate += key + '/'
                        valid_input = True
                elif len(birthdate) == 3 and key in ["0", "1", "2", "3"]:
                    birthdate += key
                    valid_input = True
                elif len(birthdate) == 4:
                    birthdate += key
                    valid_input = True

                if valid_input:
                    # Update the LCD only if there's a valid input
                    lcd.clear()
                    lcd.write_string(birthdate + "\n\rthen ENTER ---->")
    return birthdate.replace('/', '')  # remove the '/' before returning

def calculate_zodiac(month, day):
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return 'Capricorn'
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return 'Aquarius'
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return 'Pisces'
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return 'Aries'
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return 'Taurus'
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return 'Gemini'
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return 'Cancer'
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return 'Leo'
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return 'Virgo'
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return 'Libra'
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return 'Scorpio'
    else:
        return 'Sagittarius'

# This function is intended to control the Game Boy
def control_external_device(birthdate):
    birth_month, birth_day = map(int, [birthdate[:2], birthdate[2:]])
    pulse_pin(START)
    time.sleep(3)
    # Navigate to each digit individually
    for i in range(abs(2 - birth_month // 10)):
        pulse_pin(DOWN)
    pulse_pin(RIGHT)
    for i in range(abs(2 - birth_month % 10)):
        pulse_pin(DOWN)
    pulse_pin(RIGHT)
    for i in range(abs(3 - birth_day // 10)):
        pulse_pin(DOWN)
    pulse_pin(RIGHT)
    for i in range(abs(3 - birth_day % 10)):
        pulse_pin(DOWN)

    # Confirm the date
    pulse_pin(START)

mode = "normal"
start_time = None

# This code will run once before entering the loop
lcd.clear()
time.sleep(0.3)
lcd.write_string(u'Insert offering\n\ror press ENTER')

while True:
    # Initial State: Wait for offering
    lcd.clear()
    time.sleep(0.3)
    lcd.write_string(u'Insert offering\n\ror press ENTER')

    offering_accepted = False
    start_time = None
    mode = "normal"

    while not offering_accepted:
        key, duration = check_keypad()

        # Handle control mode key presses
        if control_mode:
            if key in KEY_TO_PIN:
                pulse_pin(KEY_TO_PIN[key])

        # Handle normal mode
        else:
            # Check if 'wait_button' or 'C' key is pressed in normal mode.
            if GPIO.input(wait_button) == 0 or key == "C":
                lcd.clear()
                time.sleep(0.3)
                lcd.write_string(u'Offering\n\rAccepted')
                time.sleep(2)
                offering_accepted = True

    # State: Birthdate input and Zodiac calculation
    while offering_accepted:  # This loop will keep asking for birthdate until a valid one is entered.
        # Get birthdate after offering is accepted
        birthdate = get_birthdate()

        try:
            birth_month, birth_day = map(int, [birthdate[:2], birthdate[2:]])
            datetime(year=2000, month=birth_month, day=birth_day)  # this will raise an error if date is invalid
            zodiac_sign = calculate_zodiac(birth_month, birth_day)

            lcd.clear()
            lcd.write_string("Born under:\n\r" + zodiac_sign)
            time.sleep(1)
            lcd.clear()
            lcd.write_string(u'Opening the\n\rCircle')
            time.sleep(2)
            lcd.clear()
            lcd.write_string(u'   Gaze upon the\n\r<---------Oracle')
            control_external_device(birthdate)
            time.sleep(8)
            subprocess.call(["python3", "zodiac.py", zodiac_sign])
            pulse_pin(SELECT)
            lcd.clear()
            lcd.write_string(u'Closing the\n\rCircle')
            time.sleep(3)  # Adjust this delay as needed
            offering_accepted = False  # Reset the flag to return to the initial state
        except ValueError:
            lcd.clear()
            lcd.write_string(u'Invalid\n\rbirthdate')
            time.sleep(2)
            continue  # if date is invalid, continue to next iteration of the loop


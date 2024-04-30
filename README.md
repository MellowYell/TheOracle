# TheOracle
A "fortune telling" machine that runs on a Raspberry Pi Zero W, uses a custom Game Boy ROM as a display, and prints via thermal printer

# Version 2 Updates

* Put a backlit IPS display kit on the GameBoy Color and replaced the front shell
* repositioned Game Boy and LCD
* New "overlay" for the front window
* New USB thermal printer; filled old hole with a new shadowbox feature
  
# Operation
The user, after submitting their offering, is prompted by the LCD to enter their birthdate on the keypad. The code looks up their zodiac sign and passes it to another program that does the chatGPT call to request a horoscope in the literary style of HP Lovecraft/Dr. Seuss. The resulting string is converted to a bitmap, then an existing image is appended to it. The Game Boy, running a custom ROM, is controlled by relay modules that "press" the buttons and give the illusion the Game Boy is doing the divination. Finally, another program is run to connect to the printer and prints the .bmp file with the user's horoscope.

# Components
The enclosure splits in half for transport, as I had to fly with it from Idaho to San Francisco. I tried to use as many salvaged parts I had laying around as possible, such as a card slot frame from an IBM 3277 terminal (before you reach for your pitchfork, it had severe screen burn and was already parted out to help someone revive another I sold him, so I did my duty to save one from the landfill).

The keypad connector, and top to bottom connections, are via mil-spec Amphenol connectors, and a Canon connector of similar design. The upper rear compartment is a disk drive tray from the aforementioned PC case. The pinpad and LCD are salvaged from... I can't remember, to be honest.
The main power supply puts out 5V @6A, and is fused inside the box before being distributed to the printer, GameBoy, and RPi, which have their own, resettable fuses, externally accessible for the latter two.
The BLE printer was a poor choice (and has since been replaced with a mini receipt printer like the ones that Adafruit used to sell, connected via USB, but hacking the Cat printer was too juicy a proposition to pass up at the time. I've literally hacked the back off and added a spool arm to allow the use of much longer (and cheaper) rolls of receipt paper.
PXL_20230810_201341771.MP.jpg
BLE "cat" printer, inside front door with fuse

Both the printer and the coin mechanism are mounted in the door, which is hinged at the bottom. The mechanism connected to the lock latches the door at the top, and the hasp that covers the printer door further down, with a single turn of the key. 

# CREDITS
ROM
https://julss.itch.io/
Fiverr - @juls_fiv
Thermal Printer
Main source: https://github.com/amber-sixel/gb01print/blob/main/gb01print.py
Forked from: https://github.com/WerWolv/PythonCatPrinter

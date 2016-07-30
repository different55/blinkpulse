# Original script by: Will Yager
# http://yager.io/LEDStrip/LED.html
# Mod by Different55 <burritosaur@protonmail.com>
# Seriously he did like 99% of the work here, all I changed was the device it
# outputs to and changed the way it outputs the info. This dude's amazing,
# definitely check him out.

loop = True # Whether or not to pulse from both ends of the strip. If you have a lot of LEDs (more than 8-16) I'd recommend having this on.
sensitivity = 1.3 # Sensitivity to sound.

import pyaudio as pa
import numpy as np
import sys
from blinkstick import blinkstick
import notes_scaled_nosaturation
from time import sleep, time, localtime
from colorsys import hsv_to_rgb

audio_stream = pa.PyAudio().open(format=pa.paInt16, \
								channels=2, \
								rate=44100, \
								input=True, \
								# Uncomment and set this using find_input_devices.py
								# if default input device is not correct
								#input_device_index=2, \
								frames_per_buffer=1024)

# Convert the audio data to numbers, num_samples at a time.
def read_audio(audio_stream, num_samples):
	while True:
		# Read all the input data. 
		samples = audio_stream.read(num_samples) 
		# Convert input data to numbers
		samples = np.fromstring(samples, dtype=np.int16).astype(np.float)
		samples_l = samples[::2]  
		samples_r = samples[1::2]
		yield samples_l, samples_r


stick = blinkstick.find_first()
count = stick.get_led_count()

def send_to_stick(strip):
	stick.set_led_data(0, strip)

if __name__ == '__main__':

	audio = read_audio(audio_stream, num_samples=1024)
	leds = notes_scaled_nosaturation.process(audio, num_leds=32, num_samples=1024, sample_rate=44100, sensitivity=sensitivity)
	
	if loop:
		data = [0]*int(count/2)*3
		data2 = [0]*int(count/2)*3
	else:
		data = [0]*count*3
	
	sent = 0
	for frame in leds:
		brightest = 0
		for i, led in enumerate(frame):
			if led > frame[brightest]:
				brightest = i
		
		hue = brightest/48.0
		
		color = hsv_to_rgb(hue, 1, min(frame[brightest]*1.2, 1))
		
		del data[-1]
		del data[-1]
		del data[-1] # I feel dirty having written this.
		if loop:
			del data2[0]
			del data2[0]
			del data2[0]
		
		color = [int(color[1]*255), int(color[0]*255), int(color[2]*255)]
		
		data = color + data
		
		if loop: # finaldata exists because if I try to do the seemingly sane thing it breaks.
			data2 = data2 + color
			finaldata = data+data2
		else:
			finaldata = data
		
		now = time()
		if now-sent < .02:
			sleep(max(0, .02-(now-sent)))
		
		sent = time()
		send_to_stick(finaldata)

# IDEAS:
# Accelerate movement with amplitude?
# Draw bars sized according to loudness and colored according to frequency
# Draw just one bar sized according to loudness and ^
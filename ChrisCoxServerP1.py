#!/usr/bin/env python
# Created by: Chris Cox
# Project 1
# ECE 4564
# Credit goes to: SHAWNHYMEL
import socket
import time
import thread
import threading
import RPi.GPIO as GPIO

# GPIO pin number of LED according to spec; GPIO pin 18 Phys Pin 12
LED = 12

TCP_IP = '192.168.0.12'
# TCP_IP = '0.0.0.0'
TCP_PORT = 45678
BUFFER_SIZE = 2  # Normally 1024, but we want fast response

# Setup GPIO as output
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)

# defining my thread function
# def blinkLED():
    #turn LED on
    #turn LED off
    #turn LED on
    #etc.

try:
    while 1:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)

        conn, addr = s.accept()
        print 'Connection address:', addr
        while 1:
            recv_data = conn.recv(BUFFER_SIZE)
            print "received data: ", recv_data
            if recv_data == '0': # If receive 0 turn LED OFF
                print "INSIDE '0' of IF"
                GPIO.output(LED,GPIO.LOW)
                send_data = '0'
                conn.send(str(send_data))  # Send ACK to RPI1
                GPIO.cleanup()
                conn.close() # Close socket connection
            elif recv_data == '1': # If receive 1 turn LED ON
                print "INSIDE '1' of ELIF"
                GPIO.output(LED,GPIO.HIGH)
                send_data = '0'
                conn.send(str(send_data))  # Send ACK to RPI1
                GPIO.cleanup()
                conn.close() # Close socket connection
            elif recv_data == '2':           # This is just for now, will need to incorporate thread here; If receive 2 blink LED
                # blinkLED()
                print "INSIDE '2' of ELIF"
                GPIO.output(LED,GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(LED,GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(LED,GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(LED,GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(LED,GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(LED,GPIO.HIGH)
                send_data = '0'
                conn.send(str(send_data))  # Send ACK to RPI1
                GPIO.cleanup()
                conn.close() # Close socket connection
            # else :
                # print "INSIDE ELSE"
                # GPIO.output(LED,GPIO.HIGH)
                # time.sleep(0.5)
                # GPIO.output(LED,GPIO.LOW)
                # time.sleep(0.5)
                # GPIO.output(LED,GPIO.HIGH)
                # send_data = '1'
                # conn.send(str(send_data))  # Send ACK to RPI1
except KeyboardInterrupt:
        GPIO.cleanup()
        conn.close() # Close socket connection

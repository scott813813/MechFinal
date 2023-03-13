import pyb

# Set up a pin as an output and control it
pinC0 = pyb.Pin (pyb.Pin.board.PC0, pyb.Pin.OUT_PP)
button = pyb.Pin(pyb.Pin.board.PC13, pyb.Pin.IN)

pinC0.low()

buttonSet = True

while True:
    #print(button.value(), buttonSet)
    if button.value() == False and buttonSet == True:
        #pinC0.high()
        print('Button Pressed, Toggling Pin')
        if pinC0.value() == True:
            pinC0.low()
            buttonSet = False
            print('Pin off')
            
        elif pinC0.value() == False:
            pinC0.high()
            buttonSet = False
            print('Pin on')
            
    if button.value() == True:
        buttonSet = True
    
            

'''
pinC0.high()
print('Pin On')
print(pinC0.value())
pinC0.low()
print('Pin Off')
print(pinC0.value())
'''
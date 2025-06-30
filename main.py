import os

import eel

eel.init("www") #this is will point the directory basically will get to mnow that we have HRMLS And CSS in www

os.system('start msedge.exe --app="http://localhost:8000/index.html"')

eel.start('index.html', mode=None, host='localhost', block= True)

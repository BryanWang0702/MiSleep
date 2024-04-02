import sys
import os
sys.path.append(os.getcwd()+'\misleep')
print(os.getcwd())

from misleep.gui.show import show
    
if __name__ == '__main__':

    show()
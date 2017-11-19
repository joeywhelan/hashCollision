'''
Created on Nov 18, 2017

@author: Joey Whelan
'''
import hashlib
import time
import multiprocessing as mp
import math
import string

totalBits = 256  #bit length of sha256 digest
collisionBits = 23 #number of leading bits to have 0's
mask = (1<<totalBits) - (1<<totalBits-collisionBits) #create a mask with upper bits (# of collision bits) set to 1
textInput = None #global used to pass input string to a pool of worker processes

def singleProcessHash(text):
    """Single process version of function to find a partial hash collision on string  
        
        Args:
            text: The input string
            
        Returns:
            The input string concatenated with the number that yields the partial hash collision
        
        Raises:
            None
    """
    count = 0    
    ti = time.time()
    
    while True:
        msg = text + ':' + str(count)
        dig = hashlib.sha256(msg.encode(encoding='utf_8', errors='strict')).hexdigest()
        res = int(dig,16) & mask
        if res == 0:
            break   
        count+=1
            
    print('Single-process run time: {:0.4f}'.format(time.time()-ti))
    print ('Message: ', msg)
    return msg
        
def init(text):
    """Init function to set the input string for a pool of worker process 
        
        Args:
            text: The input string
            
        Returns:
            None
        
        Raises:
            None
    """
    global textInput
    textInput = text
    
def findCollision(arg):
    """Function called by a pool worker processes to test for partial hash collision on given input string and number
        
        Args:
            arg: The number to be concatenated to the input string and then tested for a partial hash collision
            
        Returns:
            If partial collision exists, returns that string.  Otherwise, returns nothing.
        
        Raises:
            None
    """
    global textInput
    msg = textInput + ':' + str(arg)
    hsh = hashlib.sha256(msg.encode(encoding='utf_8', errors='strict')).hexdigest()
    res = int(hsh,16) & mask
    if res == 0:
        return msg

def multiProcessHash(text):
    """Multi-process version of a partial hash finding function
        
        Args:
            text: The input string
            
        Returns:
            The input string concatenated with the number that yields the partial hash collision.
        
        Raises:
            None
    """
    mult = 1
    numValues = 10**6
    chunkSize = math.ceil(numValues/mp.cpu_count())
    found = False
    msg = None
    ti = time.time()
   
    pool = mp.Pool(initializer=init, initargs=[text])
    while not found: 
        sample = range(numValues*(mult-1), numValues*mult)
        mult += 1
        results = pool.imap_unordered(findCollision, sample, chunkSize)
        for msg in results:
            if msg:
                pool.terminate()
                pool.join()
                found = True
                break

    print('Multi-process run time: {:0.4f}'.format(time.time()-ti))
    print('Message: ', msg)
    return msg

if __name__ == '__main__':
    singleProcessHash(string.ascii_uppercase)
    print()
    multiProcessHash(string.ascii_uppercase)  
            
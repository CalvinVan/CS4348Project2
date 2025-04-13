import threading
import time
import random
from queue import Queue

#Constant factors specified in the project
NUM_TELLERS = 3
NUM_CUSTOMERS = 5 #For now I will use a smaller amount of tellers to reduce the number of output
MAX_CUSTOMERS_ENTER = 2 # Enter / Line Constraint
MAX_SAFE = 2 # Max # of tellers in safe allowed at at a time

#set up the semaphores for the shared resources
bankOpen = threading.Event() #Here we signal that the bank is open
safeAccess = threading.Semaphore(MAX_SAFE) #Here we initialize a semaphore saying that only 2 people are allowed in the safe
managerAccess = threading.Semaphore(1) # Here we initalize another semaphore saying that only 1 person/thread allowed to access manager
doorAccess = threading.Semaphore(MAX_CUSTOMERS_ENTER) #Semaphore / shared resource of limit 2 as only 2 can enter at a time


#Set up semaphores for the tellers 
# Now because each teller is its own resource, we will need an array to hold each semaphore
# corresponding to each teller at semaphore 0 since we are at neutral state
'''
The following are the conditions that tellers need to keep track of.
1. Whether they are open
2. Whether they have been assigned to a customer
3. Whether they have requested a transaction to the customer
4. Whether they have been provided a transaction by the customer
5. Whether the transaction has been completed
6. Ehether the customer has left yet to open again

'''

tellerOpen = [threading.Semaphore(0) for _ in range(NUM_TELLERS)] 
tellerCustomerAssigned = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
tellerTransactionReq = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
tellerTransactionProv = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
tellerTransactionCompleted = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
customerDepart = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]

#State Variables
tellerDictionaryArr = [{"customerID": None, "transaction": None} for _ in range(NUM_TELLERS)]
tellersReadyCount = threading.Semaphore(0)

#Thread Function Definition
def tellerThread(tellerID):
  print("HI")

def customerThread(customerID):
  print("HI")


def main():
  #First we want an array to hold our teller threads and our customer threads

  #tellerThread intialization. For now I will make basic functions to handle the the respective teller and customer threads

  tellerThreadsArr = [] #Var to manage the teller threads

  for i in range(NUM_TELLERS):
    t = threading.Thread(target=tellerThread, args=(i,)) # Here we initalize the thread saying that the thread is correlated with the function and passing in i as the teller thread's id
    tellerThreadsArr.append(t) #append the new thread to the array
    t.start()  #Start the thread
  
  time.sleep(0.1) #Here I am just having a short pause so that the tellers can get ready before initializing customers

  customerThreadsArr = []
  for i in range(NUM_CUSTOMERS):
    t = threading.Thread(target = customerThread, args=(i,))
    customerThreadsArr.append(t)
    t.start()




if __name__ == "__main__":
  main()


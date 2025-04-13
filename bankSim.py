import threading
import time
import random
'''from queue import Queue'''

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
'''customerLine = Queue() #customer line is handeled by a queue'''


#Set up customer line using array instead of queue
customerLine = []
lineLock = threading.Lock() #Want to use a lock to manage the lock safely between the threads

#Setting up structure to indicate available tellers
availableTellers = set()
tellersLock = threading.Lock()

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

tellersReadyCount = threading.Semaphore(0) # Count of tellers that are ready to serve
tellerCustomerAssigned = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
tellerTransactionReq = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
tellerTransactionProv = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
tellerTransactionCompleted = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
customerDepart = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]


#State Variables
tellerDictionaryArr = [{"customerID": None, "transaction": None} for _ in range(NUM_TELLERS)]
customerServed = 0 #Counter to manage how many customers have been served so far
customerServedLock = threading.Lock() #Lock to safely change the customerServed var

#Need assignment events indicating when a customer is assigned and an array indicating which teller the customer was assigned
CustomerAssignedEventArr = [threading.Event() for _ in range(NUM_CUSTOMERS)] #May change this up later as customers pick a teller.
CustomersAssignedTellerArr = [-1] * NUM_CUSTOMERS 

#Thread Function Definition
def tellerThread(tellerID):
  #Tellers can globally keep track fo customers served
  global customerServed

  #Set up printing out that the tellers are ready to work
  print(f"Teller {tellerID} []: ready to serve")

  #setup logic that they are ready to serve. To do this, I will refer to the semaphore used in the state variables initialized earlier

  print(f"Teller {tellerID} []: waiting for a customer")
  tellersReadyCount.release() #We will increment the semaphore to indicate how many are ready

  #Now that all the tellers are ready, we need to indicate that the bank is open for customers to start entering
  
  #Before we open the bank, I am going to utilize another lock to handle serving the customers properly
  with customerServedLock:
    if tellersReadyCount._value == NUM_TELLERS: #check for the value of our semaphore and if all the tellers are ready that means we can open the bank
      bankOpen.set()
  
  #Next we want to signal that the tellers are available to serve
  with tellersLock:
    availableTellers.add(tellerID)

  #now we will loop continuously till all customers have been served but will do later
  
def customerThread(customerID):
  #First thing seen on the sample output is that each customer will randomly pick a transaction type
  transactionType = random.choice(["Withdrawal", "Deposit"])
  print(f"Customer {customerID} []: wants to perform a {transactionType} transaction ")

  #Now setting up going to bank, entering bank, and entering line

  #random wait
  waitTime = random.randint(0,100) / 1000 #the random wait of 0-100 ms
  time.sleep(waitTime) #Wait time for travelling to the bank
  print(f"Customer {customerID} []: going to bank.")

  

  #Bc the tellers will need to tell the customer threads when they are all ready before the bank is open, we need a condition here marking when the bank is open
  if not bankOpen.is_set():
    bankOpen.wait() #wait till the bank is opened by the tellers

  
  doorAccess.acquire() #Customer will then check the semaphore condition of allowing only 2 resources into the door at a time before entering into the bank
  print(f"Customer {customerID} []: entering bank.")

  #After we enter the bank, we need to enter the line
  print(f"Customer {customerID} []: getting in line.")

  with lineLock: #Adding the customer thread into the array which is our line
    customerLine.append(customerID)
 
  doorAccess.release() #Make more "space" in the door access semaphore to allow other threads to enter

 





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

  #We need to set up the join loops to ensure that threads will properly do their execution whether
  #it be waiting or executing before the other threads proceed

  for t in customerThreadsArr:
    t.join()

  for t in tellerThreadsArr:
    t.join()
  
  #Because tellers indicate when to close the bank, we have them go after customers.

  #Once the tellers are completely done, that means the bank is closing.

  print("The bank closes for the day.")



if __name__ == "__main__":
  main()


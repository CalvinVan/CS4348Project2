import threading
import time
import random


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



#Set up customer line using array instead of queue
customerLine = []
lineLock = threading.Lock() #Want to use a lock to manage the lock safely between the threads
lineCondition = threading.Condition(lineLock) #Condition in which the threads know of the line and updating it

#Setting up structure to indicate available tellers
tellerAvailable = [threading.Event() for _ in range(NUM_TELLERS)] #Event array indicating to customers when there could be a teller available
tellerSelected = [threading.Event() for _ in range(NUM_TELLERS)] #Event Array indicating when the teller is selected by a customer
tellerLock = threading.Lock() # Lock to manage updating the teller info

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
6. Whether the customer has left yet to open again
'''

tellersReadyCount = threading.Semaphore(0) # Count of tellers that are ready to serve
tellerCustomerAssigned = [threading.Event() for _ in range(NUM_TELLERS)] # This is for when the teller has a customer and is ready
tellerTransactionReq = [threading.Event() for _ in range(NUM_TELLERS)] #Teller is requesting transaction
tellerTransactionProv = [threading.Event() for _ in range(NUM_TELLERS)] #Teller has been given transaction
tellerTransactionCompleted = [threading.Event() for _ in range(NUM_TELLERS)] #Transaction is completed and waiting for customer to leave
customerDepart = [threading.Event() for _ in range(NUM_TELLERS)] #Customer has left and can reenter ready state afterwards


#State Variables
tellerDictionaryArr = [{"customerID": None, "transaction": None} for _ in range(NUM_TELLERS)]
customerServed = 0 #Counter to manage how many customers have been served so far
customerServedLock = threading.Lock() #Lock to safely change the customerServed var
allServed = threading.Event() #Initialzing a final event which indicates when all the customers have been served and program can end
tellerExitBarrier = threading.Barrier(NUM_TELLERS) #Barrier to ensure teller threads leave at the same time



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
  
  #Now we can modify our event array and setting / signaling that the tellers are available
  tellerAvailable[tellerID].set()

  while not allServed.is_set():
    tellerSelected[tellerID].wait() #We're waiting for when the teller is selected
    tellerSelected[tellerID].clear()

    tellerCustomerAssigned[tellerID].wait() #We are waiting for the customer to introduce themself
    tellerCustomerAssigned[tellerID].clear()
    
    if allServed.is_set():
      break

    customerID = tellerDictionaryArr[tellerID]["customerID"] #Get the customer id from the state dictionary
    print(f"Teller {tellerID} [Customer {customerID}]: serving a customer")

    print(f"Teller {tellerID} [Customer {customerID}]: asks for transaction")
    tellerTransactionReq[tellerID].set() #Now we set the phase that the teller is requesting a transaction

    tellerTransactionProv[tellerID].wait() #Now we wait for the transaction to be provided by the customer
    tellerTransactionProv[tellerID].clear() #Then we unset theh transaction provided since the customer has told us what transaction they want

    transactionType = tellerDictionaryArr[tellerID]["transaction"]
    print(f"Teller {tellerID} [Customer {customerID}]: handling {transactionType} transaction")

    #logic to handle withdrawing
    if transactionType == "withdrawal":
      print(f"Teller {tellerID} [Customer {customerID}]: going to the manager")
      managerAccess.acquire() #Get manager to talk to or wait until is free
      print(f"Teller {tellerID} [Customer {customerID}]: getting manager's permission")
      time.sleep(random.randint(5,30) / 1000) #represent the random ammount of time interacting with manager
      print(f"Teller {tellerID} [Customer {customerID}]: Got permission from manager")
      managerAccess.release() #manager is now free to talk to
    
    #else we can just go to the safe regularly because the deposit doesn't need permission and nothing special

    print(f"Teller {tellerID} [Customer {customerID}]: going to safe")
    safeAccess.acquire() #Try to access safe if there is space else wait
    print(f"Teller {tellerID} [Customer {customerID}]: enter safe")

    #random time to finish the transaction
    time.sleep(random.randint(10, 50) / 1000)
    print(f"Teller {tellerID} [Customer {customerID}]: leaving safe")
    safeAccess.release() #open space for safe

    print(f"Teller {tellerID} [Customer {customerID}]: finishes {transactionType} transaction")

    print(f"Teller {tellerID} [Customer {customerID}]: wait for customer to leave")
    
    tellerTransactionCompleted[tellerID].set() #Signal to customer that transaction is done

    customerDepart[tellerID].wait() #phase/state array saying that teller is currently waiting for customer to leave before being opened again
    customerDepart[tellerID].clear() #clear it so it knows its not waiting for a customer to depart now
    tellerDictionaryArr[tellerID]["customerID"] = None #Need to also set the customerID and transaction type to None as it is available again
    tellerDictionaryArr[tellerID]["transaction"] = None

    with customerServedLock: #safely manage updating the customers being served
      customerServed += 1
      if customerServed >= NUM_CUSTOMERS:
        allServed.set()

    #indicate that the teller is ready to serve and waiting for a customer    
    print(f"Teller {tellerID} []: ready to serve")
    print(f"Teller {tellerID} []: waiting for a customer")
    tellerAvailable[tellerID].set() #Need to reset it to signal that the teller is available

    
    with lineCondition:
      lineCondition.notify_all() #need to notify the customers that one of the tellers is now free

  #If all the customers have been served, then we can say that the teller is now leaving and ending
  tellerExitBarrier.wait() #Here I implement a barrier to ensure that all the tellers leave at the same time
  with tellerLock:
    print(f"Teller {tellerID} []: leaving for the day")

          
          
  
def customerThread(customerID):
  #First thing seen on the sample output is that each customer will randomly pick a transaction type
  transactionType = random.choice(["withdrawal", "deposit"])
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

  doorAccess.release() #Make more "space" in the door access semaphore to allow other threads to enter

  #After we enter the bank, we need to enter the line
  print(f"Customer {customerID} []: getting in line.")

  with lineCondition: #while there is some condition of being in line we will continue forwards
    customerLine.append(customerID) #Add thread into the line

    while True: #while we are in line, we need to check if are at the front of the line
      
      if customerLine[0] != customerID: #If we are not then we will wait and continue till we are at the front again
        lineCondition.wait()
        continue
      
      print(f"Customer {customerID} []: selecting a teller.")

      #logic to select a teller

      selectedTeller = None
      for tellerID in range(NUM_TELLERS): # we will check if any of the tellers are available
        
          with tellerLock: #using teller lock to safely modify the conditions and assign teller
            if tellerAvailable[tellerID].is_set(): #if there is a teller available then we will clear it as not available and then assign the teller
              tellerAvailable[tellerID].clear() #need to clear it to claim the teller
              selectedTeller = tellerID
              break #We should then break out the loop since we found a teller to assign to the customer thread

      if selectedTeller is not None:
        customerLine.pop(0) #remove the thread's id from the customer line
        lineCondition.notify_all() #Signal that the line has been updated
        break
      lineCondition.wait() #We will then wait until the line condition changes from being assigned a teller
  
  print(f"Customer {customerID} [Teller {selectedTeller}]: selects teller")
  tellerSelected[selectedTeller].set()

  print(f"Customer {customerID} [Teller {selectedTeller}]: introduces itself")
  tellerDictionaryArr[selectedTeller]["customerID"] = customerID
  tellerCustomerAssigned[selectedTeller].set()

  tellerTransactionReq[selectedTeller].wait() #we need to wait for teller to ask for the transaction
  tellerTransactionReq[selectedTeller].clear()

  #Then we tell the transaction to the teller
  print(f"Customer {customerID} [Teller {selectedTeller}]: asks for {transactionType} transaction")
  tellerDictionaryArr[selectedTeller]["transaction"] = transactionType
  tellerTransactionProv[selectedTeller].set() #we set that the teller has now been provided a transaction

  tellerTransactionCompleted[selectedTeller].wait() #we need to wait for the transaction to be completed by the teller
  tellerTransactionCompleted[selectedTeller].clear()
  #logic below handles exiting the bank
  print(f"Customer {customerID} [Teller {selectedTeller}]: leaves teller")
  customerDepart[selectedTeller].set() #Now we signal the teller that the customer has left and can reset 

  print(f"Customer {customerID} []: goes to door")

  doorAccess.acquire() #Check if theres space to go through the door
  print(f"Customer {customerID} []: leaves the bank")
  doorAccess.release() #Open up space once they have left the bank
    

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
  
  allServed.set() #Once all the customer threads have been joined, this indicates that there are no more customers left

  #Here we are making sure that all of the threads are not stuck waiting on any of the events so they can start leaving and closing the bank
  for tellerID in range(NUM_TELLERS): 
    tellerSelected[tellerID].set()
    tellerCustomerAssigned[tellerID].set()
    tellerTransactionProv[tellerID].set()
    customerDepart[tellerID].set()

  for t in tellerThreadsArr:
    t.join()
  #Because tellers indicate when to close the bank, we have them go after customers.
  #Once the tellers are completely done, that means the bank is closing.
  print("The bank closes for the day.")



if __name__ == "__main__":
  main()


# Project 2 Develog Calvin Van CTV210001 CS4348.003

## April 10th 4:20 PMs
Begin reading project requirements to gain an idea of the steps and functionalities needed.

### Project Requirement Notes
Reading the description we have a couple of entities that can be represented as threads / areas of access that we are concern with
- We have 3 tellers (could be process threads or something that take in requests)
- We have customers which could be inputs / calls to access the thread. So some intuition is that the main program managing the threads can send the customers to the available threads when there is one. The customers are also able to make 2 type of requests withdraw and deposit which ii'll delve into more later. There are 50 customers and once they have been served, they leave the bank and the bank is "closed" which means the program is over.
- There is a safe in which only 2 tellers / threads are allowed in. Furthermore, if they want to go into the safe to withdraw money, they must ask the bank manager / the main program / some master thread? if they are allowed into the safe to withdraw money. However, the manager can only talk to one thread at a time.

Since we are using python, we will be utilizing the threading module and threading.semaphore for syncing.

The program will launch 3 threads for tellers and 50 threads for customers.

The shared resources will be the safe and the manager which should be protected by semaphores Other semaphores should also be needed to sync the behavior of the threads. FOr example, the customer should not leave until the Teller has finished thier transation.

Some Teller Thread details
1.  The teller has a unique id and there are 3 of them and the steps below outline their logic
- Teller will let everyone know if it is ready to serve
- **WAIT** for a customer to approach it in the mean time
- when **SIGNALED** by a customer, teller requests transaction type
- **WAIT** until the customer gives a transaction
- If transaction is a withdrawal, go to manager **SIGNAL** Manager should always give permission but there is time interacting with teller. To represent this, the teller should **SLEEP** for a random duration from 5 to 30 seconds after signaling to manager?
- Afterwards thread is allowed to access the safe, It should **WAIT** if it is occupied by the two tellers
- Once in the safe, the teller will physically perform transaction (represented by **SLEEPING** for a random duration between 10 and 50 ns)
- **SIGNAL** customer saying that the transaction is done
- **WAIT** until the customer leaves the teller and become available again **SIGNAL**


Customer Details
There are 50 customers and they do the following actions
- The customer randomly decides what transaction to perform: deposit or withdrawal
- The customer then **WAITS** between 0-100ms
- The customer then enters the bank **SIGNAL?** The door only allows two customers to enter at a time
- The customer wil then get in line. If there is an available teller then the customer will go to said teller else it will **WAIT** until it is called and then go the teller
- It should then give its id to the teller
-The customer will **WAIT** for the teller to ask for the transaction
- THe customer will tell the teller the transaction
- The customer will **WAIT** for the teller to complete transaction
- The customer will leave the bank through the door and simulation (end thread)


Output:
The teller and customer threads print out a line for each simulated action they are performing and use the format
{Thread Type ID} [Thready_TYPE ID] : MSG

Example:
Customer 10 [Teller 0]: selects teller

If there is any block for an amount of time there are 2 lines.
THe first line is the action being taken before the wait
The other is after the wait
So it should be 
Thread Type ID: Waiting for action
Thread Type ID: Done Wait and Action Completed



## April 11th 6:00 PM
### Continue highlighint requirements

If there is a shared resource being accessed (the manager or safe), then 3 lines are outputted.

1. Indicate the teller going to the resources
2. Indicate the thread that is using the resource
3. Inidicate when the thread is done using the resource.

Let's outline the line of actions taken

1. Initialize the teller and customer threads
2. Initialize the shared resources that is the safe and the manager

3. Tellers will need to signal customer threads that they are waiting for a customer
3b. Customers will have to be entered into the system and randomly decide between deposit and withdrawal and then wait before entering the bank in which they can get in line.

Continue onwards as I want to start some coding now.

Start setting up the threads and semaphore states.

As for how I will setup the semaphores, for more open shared resources that can be accessed by the teller threads, I will initialize them through the threading.semaphore(# of allowed threads)

As for the teller semaphores, they need to be treated differently as each teller needs to be its own resource so an array will be needed to hold the semaphore for each teller which has a number of conditions mentioned in the code of the rogram.


In addition to the state of the semaphores, I will look into using a variable to hold the states such as the teller who has to hold onto the transaction type that it has and the customer ID, an array filled with dictionaries keyed by the customerID and transaction string will work for easy access and the number of available tellers.


## April 12th 6:50 PM
## Start setting up main function to initialize threads
Will start setting up the arrays to manage our teller and customer threads.

For now I will have the thread functions be bare minimum to allow for some initializationa nd will focus on communication afterwards.


**SPECIAL NOTE** I forgot to mentioned but somewhere when brainstorming up how to manage customers to properly enter and exit out of the lines is to use a queue which is why queue was imported ahead of time but might remove this later as I can possibly sync the teller and customer threads without having to use it.

## April 12th 10:05PM 
## Recontinue working on setting up threads
- Setup join functions for threads to finish executing and waiting properly
- Setup end print statement
-  Start working on setting up the teller and customer threads to initialize their states and transaction types


## April 13 12:00 PM
## Start setting up thread communication between the tellers and customers
- I decided to remove the use of a queue and simplify it by using an array and set instead to manage the customers in line and the tellers that are available.
- Realizing that I was setting it up to where the events handeled it such that the teller was selecting the customer but after looking at the sample output that the customer is selecting the teller and not the other way around so need to modify program and its events

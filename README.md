# CS4348Project2

The program utilizes only one main file which is the bankSim.py
To run the program, just run "python bankSim.py"

As for the functionality of the program, the program intializes 3 teller threads set by a constant and 50 customer threads set by a constant. Using the teller thread and customer thread function definitions, it organizes the communication between the teller and customer threads. In addition, the program utilizes semaphores to manage shared resource access and event systems to indicate when teller and customer threads are allowed to proceed and stop writing. 

A note to give about the program is that outputs are formatted below as
Actor_Thread_Type {Actor_Thread_ID} [Actee_Thread_type Actee_Thread_ID]: MSG

where the actor is the one performing the action and actee is the one for which the actor is communicating with / doing the action for given the msg (message).

Using the program is quite simple, you can just simply type the command above in the prompt and it will run the bank simulation which uses randomly generated transaction types to proceed. 
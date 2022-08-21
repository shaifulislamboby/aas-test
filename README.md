# Test Case Generation for Asset Administration Shell REST APIs

The digital twin, or more precisely the Asset Administration Shell (AAS), is the key element for interoperability in 
Industrie 4.0. Together with the asset, it forms the I4.0 component. There are three different interfaces to access the
AAS being a REST API one of them. To ensure interoperability of a given API it is necessary to ensure its compliance to
the standard. This is done by testing the API. However, specifying test cases manually is costly and error-prone.
That is why generating test cases automatically is desired. In this work existing test case generation methods for 
REST APIs shall be evaluated and extended for the testing of AAS REST APIs.
The thesis has to work on the following tasks:

1. Evaluation of REST API test generation methods 
2. Selection of the appropriate method for this task based on criteria
3. Prototyping of an AAS REST API test case generator
4. Evaluation of the test case generator 
5. Discuss the test results and document the content of the tasks. 


## For running the test please follow the steps bellow
### first you have to make sure that your FAAAST server is up and running
- To do so please go to the `FAAAST_SERVICE` directory via `cd FAAAST_SERVICE` 
- then in terminal execute `docker-compose up` for firing up the server

### Once you have running the server you can now run the test suits by following these steps:
- in `aas` directory there is a main.py file where you can modify the server base url, id, password etc 
- that might be required for accessing the endpoint of that server.
- If your server is open to all then you don't have to add any id or password 
- You have to specify the base_url there in the main function 
- The location of the openapi specification of the AAS also need to mentioned in that function, this is required as 
  the program will load the specification from that location.
- You also can add a name of the output file name, where all the tests results will be written down after running the
  tests.

#### Once all the steps that are mentioned above are done then, you can simply run that main.py file
###  to start that test suits
- to so just run `python aas/main.py`

### :fire: Viola that goes :fire:
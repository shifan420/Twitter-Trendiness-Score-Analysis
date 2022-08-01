In server.py, we've written code to warn failures including HTTPError(Trouble with requesting the url) and ConnectionError(losing internet connection) and to recover from such failures. <br />
For HTTPError, error code 429 (Too many request) is the only error we encountered, so we decided to write a chuck of code in server.py to deal with "Too many request"(request_status_code = 429) issue. Basically, when we run the code and get into the API requesting step, it'll show us the rate limits left. If we have no rate limits left, then it'll calculate the remaining time that allows us to request the url again and suspends execution for the given remaining time. Once we are shown a new command line, we can rerun the code to request API again<br />
For ConnectionError, we use try except to catch the error in the main function. When you disconnect the network, it'll tell users that there is a connection issue and stop execute the code.<br />
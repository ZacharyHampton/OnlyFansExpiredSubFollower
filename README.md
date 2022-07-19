# Onlyfans Expired Subscriber Follower

### Requirements
1. Download program using git clone or download as zip.
```git clone github.com/ZacharyHampton/OnlyFansExpiredSubFollower```
2. Have python version >= 3.10.
3. Install requirements.
```python3 -m pip install -r requirements.txt```
4. Obtain onlyfans cookies, x-bc header & browser user agent.

## How to obtain required data:
1. Log into onlyfans
2. Open chrome devtools (ctrl+shift+i)
3. Go to network tab.
4. Turn on XHR Filtering
5. Refresh page, and view any request made to *.onlyfans.com
6. You will be able to see the request headers. The cookies, user-agent & x-bc headers are all there.

## Important:
Make sure all of these values don't include their key when inputted into the program ("Cookies: ", "x-bc ", "User-Agent: ")

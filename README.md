edit-along
===========

A collaborative text editor implementing 
Neil Fraser's 
[differential synchronization algorithm](https://neil.fraser.name/writing/sync/)
as a `Python` server with `JS` client.

## Dependencies

- [`bottle`](https://github.com/bottlepy/bottle) for routes
- [`gevent`](http://www.gevent.org/) and [`gevent-websocket`](https://gitlab.com/noppo/gevent-websocket) for WebSocket
- [`google-diff-match-patch`](https://code.google.com/archive/p/google-diff-match-patch/) is included 

Install with:
```shell
 pip install -r requirements.txt 
```


## Quick Start

Start the server:
```shell
cd ./py && python3 server.py
```

Open a browser and visit [http://localhost:8080/](http://localhost:8080/).
Copy/paste the generated url in a new tab or two.

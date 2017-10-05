edit-along
===========

A collaborative text editor implementing 
Neil Fraser's 
[differential synchronization algorithm](https://neil.fraser.name/writing/sync/)
as a `Python` server with `JS` client.

## Dependencies

The Docker container includes all dependencies.

If not using Docker, running:
```shell
 pip install -r requirements.txt 
```

...will install:

- [`bottle`](https://github.com/bottlepy/bottle) for routes
- [`gevent`](http://www.gevent.org/) and [`gevent-websocket`](https://gitlab.com/noppo/gevent-websocket) for WebSocket
- [`google-diff-match-patch`](https://code.google.com/archive/p/google-diff-match-patch/) is included 


## Quick Start

```shell
./go
```

Open a browser and visit [http://localhost:1070/](http://localhost:1070/).
Copy/paste the generated url in a new tab or two.


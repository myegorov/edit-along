edit-along
===========

A collaborative text editor implementing 
Neil Fraser's 
[differential synchronization algorithm](https://neil.fraser.name/writing/sync/)
as a `Python` server with a `JS` client. The implementation is functionally
complete, but does not address all the network failure scenarios considered
by Fraser. A caveat is in order: The project was conceived as an 
experiment in using coroutines/continuations in Python. I haven't had 
a chance to clean or tighten up the code since.

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

## License

This repository is licensed under the 
[MIT license](https://opensource.org/licenses/MIT), except for
`./py/diff_match_patch.py` and `./static/js/diff_match_patch.js` 
which are licensed under 
[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
The default `Match_Threshold` has been modified from the original 
`diff_match_patch.py` 
[source](https://github.com/google/diff-match-patch/blob/master/python3/diff_match_patch.py).

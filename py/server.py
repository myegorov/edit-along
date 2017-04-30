from bottle import route, run, get, static_file

@route('/')
def index():
    return static_file('index.html', root="../")

@get("/static/css/<filepath:re:.*\.css>")
def css(filepath):
    print("hello CSS")
    return static_file(filepath, root="../static/css")

@get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    print("hello JS")
    return static_file(filepath, root="../static/js")


run(host='localhost', port=8080, debug=True)

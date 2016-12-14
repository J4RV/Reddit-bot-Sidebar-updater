import socket
import re
import webbrowser
import praw
import json

# Get the config from the Json file
with open('config.json') as data_file:
    data = json.load(data_file)

# Socket stuff
host = '127.0.0.1'
port = 65010
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(1)  # don't queue up any requests


def init():
    if data["REFRESH_TOKEN"]:
        reddit = praw.Reddit(client_id=data["CLIENT_ID"],
                             client_secret=data["CLIENT_SECRET"],
                             user_agent=data["AGENT"],
                             refresh_token=data["REFRESH_TOKEN"])
    else:
        reddit = praw.Reddit(client_id=data["CLIENT_ID"],
                             client_secret=data["CLIENT_SECRET"],
                             user_agent=data["AGENT"],
                             redirect_uri=data["REDIRECT_URI"])
        request_token(reddit)

    return reddit


def request_token(reddit):
    link_refresh = reddit.auth.url(['identity modconfig read'], 'permanent')
    webbrowser.open_new(link_refresh)
    csock, caddr = sock.accept()
    req = csock.recv(1024)  # get the request, 1kB max
    req = req.decode("utf-8")

    print(req)

    match = re.search('code=(.+)\sHTTP', req)

    if match:
        global REFRESH_TOKEN

        code = match.group(1)
        REFRESH_TOKEN = reddit.auth.authorize(code)
        print("Refresh token: ", REFRESH_TOKEN)

        #Update the token in the json
        with open('config.json', 'w') as write_file:
            data["REFRESH_TOKEN"] = REFRESH_TOKEN
            json.dump(data, write_file, indent = 4)

        csock.sendall('Bot initiated correctly!\n\nMrDestructoid'.encode())
    else:
        # If there was no recognised command then return a 404 (page not found)
        print("Returning 404 - Couldn't get the Code")
        csock.sendall("HTTP/1.0 404 Not Found\r\n".encode())

    csock.close()

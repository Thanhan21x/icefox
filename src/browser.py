import socket
import ssl
import tkinter

class URL:
    def __init__(self, url):
        self.view_source = False
        if url.startswith("view-source:"):
            _, url = url.split(":", 1) 
            self.view_source = True

        if "://" in url:
            self.scheme, url = url.split("://", 1) # extract the scheme and url
            #assert self.scheme == "http" # only support http
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443
            # separate the host from the path. 
            if "/" not in url:
                url = url + "/"
            self.host, url = url.split("/", 1)
            self.path = "/" + url

            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)

        elif url.startswith("data:"):
            self.scheme, data = url.split(":", 1)
            self.data_type, self.data = data.split(",",1)

    def request(self):
        if (self.scheme == "http" or self.scheme =="https"):
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
            # socket created -> connect it to another computer
            # for that -> provide a host and a port
            # the port -> depends on the protocal you are using;
            # for now, it should be 80.
            s.connect((self.host, self.port))
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)

            # The connection -> established
            # -> make request to tthe other server.
            # -> by sending it some data using the 
            # send method
            request = "GET {} HTTP/1.0\r\n".format(self.path)
            request += self.add_header("Host", self.host)
            request += self.add_header("Connection", "close")
            request += self.add_header("User-Agent", "icefox")
            request += self.add_header("Localtion", "/")
            request += "\r\n" ## 2 \r\n newlines -> the end
            s.send(request.encode("utf8"))

            # read the server's response
            response = s.makefile("r", encoding="utf8", newline="\r\n")
            # split the response into pieces
            statusline = response.readline()
            version, status, explaination = statusline.split(" ", 2)

            # after the status line come the headers
            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n": break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()

            # some header -> tell us that the data we're 
            # trying to access is being sent in an unsual way 
            assert "transer_encoding" not in response_headers
            assert "content_encoding" not in response_headers

            # usually, the content comes after the headers
            content = response.read()
            s.close()

            # it's the body that we're going to display,
            # return that
            return content
        elif self.scheme == "file":
            # return the content in the file provided the path
            with open(self.path, "r") as f:
                return f.read()
        elif self.scheme == "data" and self.data_type == "text/html":
            return self.data
        else:
            print("Unsupported scheme")
            # notify error, exit


    def add_header(self, header, value):
        return "{}: {}\r\n".format(header, value)

WIDTH, HEIGHT = 800, 600

HSTEP, VSTEP = 13, 18

SCROLL_STEP = 100

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)

    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for x,y,c in self.display_list:
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    
    return display_list

def lex(body):
    text = ""
    in_tag = False

    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c

    return text

def view_source(body):
    for c in body:
        if c == ">":
            print(c)
        else:
            print(c, end="")

def print_entity(entity):
    if entity == "lt":
        print("<", end="")
    elif entity == "gt":
        print(">", end="")
    else:
        print(entity, end="")



# Load a web page just by stringing together request and show


if __name__ == "__main__":
    import sys 
    default_url = "file:///home/iceman/overthewire.txt"
    
    if len(sys.argv) == 2:
        Browser().load(URL(sys.argv[1]))
        tkinter.mainloop()
    elif len(sys.argv) == 1: 
        Browser().load(URL(default_url))



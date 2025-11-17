import socket
import ssl

class URL:
    def __init__(self, url):
        # check if "://" in the url:
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

        elif "data:" in url:
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
            request += "\r\n" ## 2 \r\n newlines -> the end
            print(request)
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


# Displaying the HTML

# Take the page HTML and print all the extract
# but not the tags
def show(body):
    in_tag = False
    in_entity = False
    entity = ""
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif c == "&":
            in_entity = True
        elif c == ";":
            in_entity = False
            print_entity(entity)
            entity = ""
        elif in_entity:
            entity += c
        elif not in_tag:
            if c == "&lt;":
                print("<", end="")

def print_entity(entity):
    if entity == "lt":
        print("<", end="")
    elif entity == "gt":
        print(">", end="")
    else:
        print(entity, end="")



# Load a web page just by stringing together request and show
def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
    import sys 
    default_url = "file:///home/iceman/overthewire.txt"
    if len(sys.argv) == 2:
        load(URL(sys.argv[1]))
    elif len(sys.argv) == 1: 
        load(URL(default_url))




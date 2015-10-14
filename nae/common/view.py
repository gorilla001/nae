from webob import Response


class View(Response):
    def __init__(self, json):
        super(View, self).__init__()
        self.json = json

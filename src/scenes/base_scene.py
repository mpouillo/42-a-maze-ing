class BaseScene:
    def __init__(self, app) -> None:
        self.app = app
        self.model = None
        self.view = None

from src.views.renderers import BaseRenderer


class HexRenderer(BaseRenderer):
    def __init__(self, app, model):
        super().__init__(app, model)

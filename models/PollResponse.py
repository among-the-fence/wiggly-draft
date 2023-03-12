class PollResponse:
    @staticmethod
    def value_or_default(args, key, default):
        return args[key] if key in args else default

    def __init__(self, text = None, header = None, color = None, ephemeral = False, image = None):
        self.ephemeral = ephemeral
        self.color = color
        self.text = text
        self.header = header
        self.image = image
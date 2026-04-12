class InMemoryWarningSink:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def warn(self, message: str) -> None:
        self.messages.append(message)

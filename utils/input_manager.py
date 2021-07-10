class InputManager:
    def __init__(self, prompt, error_message, conversion):
        self.prompt = prompt
        self.error_message = error_message
        self.conversion = conversion

    def input(self):
        while True:
            try:
                value = self.conversion(input(self.prompt))
                return value
            except ValueError:
                print(self.error_message)

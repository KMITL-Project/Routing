class CustomError(Exception):
    def __init__(self, message, status, code):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        
        # Now for your custom code
        self.message = message
        self.status = status
        self.code = code
    
    def __str__(self):
        return f"{self.message} (Status: {self.status}, Code: {self.code})"
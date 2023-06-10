class Error:
    def throw(self, types: int = 99, stages: int = 99, message: str = "", suggestion: str = "") -> None:
        """ 
        Error Types:\n
        (1) Unexpected Symbol Error\n
        (2) Integer Error\n

        States:\n
        (1) Lexing Stage\n
        """

        # Define names of error types and stages.
        errorTypes = {
            1: "Unexpected Symbol Error",
            99: "Unexpected Error Type"
        }
        errorStage = {
            1: "Lexing Stage",
            99: "Unexpected Stage"
        }

        # Check if types, stages, and message exists.
        if not message: message = "No error message."
        if suggestion != "": suggestion = f"Suggestion: {suggestion}\n"
        if types not in errorTypes: types = 99
        if stages not in errorStage: stages = 99

        # Print error message.
        print(f"Error: {errorTypes[types]}\nThrowed At: {errorStage[stages]}\nError Message: {message}\n{suggestion}")

        # Exit with code -1.
        exit(-1)
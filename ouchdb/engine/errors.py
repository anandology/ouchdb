
class EngineException(Exception):
    @property
    def data(self):
        return {"error": self.error, "reason": self.args[0]}

class NotFound(EngineException):
    error = "not_found"
    
class Conflict(EngineException):
    error = "conflict"

class CompileError(EngineException):
    error = "map_compilation_error"

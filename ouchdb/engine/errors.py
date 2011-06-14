
class EngineException(Exception):
    pass
    
class Conflict(EngineException):
    error = "conflict"

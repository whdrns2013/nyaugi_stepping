from enum import Enum

class StatusCode(str, Enum):
    SUCCESS = 0
    FAIL = 1

class LogLevelType(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class LogWhen(str, Enum):
    S = "S"
    M = "M"
    H = "H"
    D = "D"
    MIDNIGHT = "midnight"
    SUN = "W{0}"
    MON = "W{1}"
    TUE = "W{2}"
    WED = "W{3}"
    THU = "W{4}"
    FRI = "W{5}"
    SAT = "W{6}"

class RequestMethod(str, Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"
    HEAD = "head"

class DataSourceType(str, Enum):
    FILE = "file"
    DB = "db",
    NOSQL = "nosql"
    INDEX = "index"

class DUPLICATION(str, Enum):
    VALID = 0
    DUPLICATED = 1
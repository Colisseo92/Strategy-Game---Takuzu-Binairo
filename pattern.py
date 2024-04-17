import enum
from utils import ErrorName

class PatternType(enum.Enum):
    
    ERROR = 0
    FORBIDDEN = 1
    GRID_PATTERN = 2
    NONE = 3
        
class Patterns(enum.Enum):
    
    OOO = ["111",None,[]]
    OZO = ["101",None,[1]]
    OOZ = ["110",None,[2]]
    ZOO = ["011",None,[0]]
    OXO = ["1-1",0,[1]]
    XOX = ["-1-",None,[0,2]]
    OOX = ["11-",0,[2]]
    XOO = ["-11",0,[0]]
    XXO = ["--1",None,[0,1]]
    OXX = ["1--",None,[1,2]]
    #--------------------------------
    ZZZ = ["000",None,[]]
    ZOZ = ["010",None,[1]]
    ZZO = ["001",None,[2]]
    OZZ = ["100",None,[0]]
    ZXZ = ["0-0",1,[1]]
    XZX = ["-0-",None,[0,2]]
    ZZX = ["00-",1,[2]]
    XZZ = ["-00",1,[0]]
    XXZ = ["--0",None,[0,1]]
    ZXX = ["0--",None,[1,2]]
    #--------------------------------
    OZXXX = ["10---",1,[3]]
    XXXOZ = ["---10",0,[1]]
    ZOXXX = ["01---",0,[3]]
    XXXZO = ["---01",1,[1]]
    
    def getPatternString(self) -> str:
        """Function that return the string object that describe the pattern

        Returns:
            str: pattern string format
        """
        return self.value[0]
    
    def getPatternPositions(self) -> list:
        """Return the position that the pattern can take

        Returns:
            list: list containing the positions
        """
        return [i for i in range(len(self.getPatternString()))]
    
    def getEmptyPositions(self) -> list:
        """Return the list of position that can be filled in a pattern

        Returns:
            list: fillable positions
        """
        return [i for i,char in enumerate(self.value[0]) if char == "-"] if "-" in self.value[0] else [0]
    
    def getSpecialPositions(self) -> list:
        """Return the list of empty position for some pattern or a random 
        position for other pattern (used for special case)

        Returns:
            list: positions
        """
        return self.value[2]
    
    def getExpectedValue(self) -> int:
        """Return the list of expected value for empty position in the pattern

        Returns:
            int: exepcted value
        """
        return self.value[1]
    
    def getSize(self) -> int:
        """Return the size of the pattern

        Returns:
            int: size of the pattern
        """
        return len(self.value[0])
    
    def getMaximumValue(self) -> int:
        """Return the value that is the most present in the pattern

        Returns:
            int: value most present in pattern
        """
        return 1 if self.value[0].count("1") >= self.value[0].count("0") else 0
    
class Pattern:
    
    def __init__(self,pattern: Patterns, pattern_type: PatternType = PatternType.NONE,error_name: ErrorName = None):
        self.pattern = pattern
        self.pattern_type = pattern_type
        self.error_name = error_name
        self.size = pattern.getSize()
    
    def getPattern(self) -> str:
        """Return the string value of the pattern

        Returns:
            str: string value
        """
        return self.pattern.getPatternString()
    
    def getPatternPositions(self) -> list:
        """Return the position that the pattern can take

        Returns:
            list: list containing the position
        """
        return self.pattern.getPatternPositions()
    
    def getEmptyPositions(self) -> list:
        """Return the list of positions that can be filled in the pattern

        Returns:
            list: fillable positions
        """
        return self.pattern.getEmptyPositions()
    
    def getSpecialPositions(self) -> list:
        """Return the list of empty position for some pattern or a random
        position for other (used for special case)

        Returns:
            list: positions
        """
        return self.pattern.getSpecialPositions()
    
    def getExpectedValue(self) -> int:
        """Return the list of expected value for empty position in the pattern

        Returns:
            int: expected value
        """
        return self.pattern.getExpectedValue()
    
    def getError(self) -> ErrorName:
        """Return the ErrorName, text that describe the error if the pattern is 
        part of an error detection

        Returns:
            ErrorName: ErrorName object
        """
        return self.error_name
        
    def getType(self) -> PatternType:
        """Return the type of the pattern, what he is used for

        Returns:
            PatternType: PatternType object
        """
        return self.pattern_type
    
    def getMaximumValue(self) -> int:
        """Return the value that is the most present in the pattern

        Returns:
            int: value the most present
        """
        return self.pattern.getMaximumValue()
    
    def setError(self,error_name: ErrorName) -> None:
        """Function to set the error name of the pattern

        Args:
            error_name (ErrorName): ErrorName object
        """
        self.error_name = error_name
        
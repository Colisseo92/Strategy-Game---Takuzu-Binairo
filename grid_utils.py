from utils import LineType,ErrorName,ErrorType
from pattern import Pattern
from HintWindow import HintType

class Position():
    
    __slots__ = ("y","x")
    
    def __init__(self,y: int,x: int):
        self.y = y
        self.x = x
        
    def getY(self) -> int:
        return self.y
    
    def getX(self) -> int:
        return self.x
    
    def getLineNumber(self) -> int:
        return self.y
    
    def getColumnNumber(self) -> int:
        return self.x

    def toTuple(self) -> tuple:
        return (self.y,self.x)     
    
    def __str__(self) -> str:
        return f"x: {self.x} y: {self.y}"
    
class Entry(Position):
    
    def __init__(self,x:int,y:int,value:int) -> None:
        super().__init__(y,x)
        self.__value = value
        
    def getDisplayableValue(self) -> str:
        """Get the value displayed in the main window"""
        return str(self.__value) if self.__value != None else ""
    
    def getValue(self) -> int:
        """Return the value of the entry"""
        return self.__value
    
    def __str__(self) -> str:
        return super().__str__() + f" | Value : {self.__value}"
    
class PatternResultForbidden():
    
    __slots__ = ("positions","empty_position","expected_value")
    
    def __init__(self,positions: list,empty_position: int,expected_value: int) -> None:
        self.positions = positions
        self.empty_position = empty_position
        self.expected_value = expected_value
        
    def getPositions(self) -> list:
        return self.positions
    
    def getEmptyPosition(self) -> int:
        return self.empty_position
    
    def getExpectedValue(self) -> int:
        return self.expected_value
    
class ForbiddenPaternPosition(Position):
    
    def __init__(self,position: Position,patternResultForbidden: PatternResultForbidden, lineType: LineType) -> None:
        Position.__init__(self,position.x,position.y)
        self.__patternResultForbiden = patternResultForbidden
        self.__lineType = lineType
        
    def getLineType(self) -> LineType:
        return self.__lineType
    
    def getPositions(self) -> list:
        return self.__patternResultForbiden.getPositions()
    
    def getExpectedValue(self) -> int:
        return self.__patternResultForbiden.getExpectedValue()
    
class GridError():
    
    __slots__ = ("error_type","error_name","position","hintType")
    
    def __init__(self,error_type: ErrorType,error_name:ErrorName,position: list, hintType: HintType):
        self.error_type = error_type
        self.error_name = error_name
        self.position = position
        self.hintType = hintType
        
    def getType(self) -> ErrorType:
        return self.error_type
    
    def getName(self) -> ErrorName:
        return self.error_name
    
    def getPositions(self) -> list:
        return self.position
    
    def getHintType(self) -> HintType:
        return self.hintType
    
    def __str__(self) -> str:
        return f"[GridError] ErrorType : {self.error_type} | ErrorName: {self.error_name} | Position : {self.position}"
    
class GridPattern():
    
    __slots__ = ("positions","lineType","pattern","line_number")
    
    def __init__(self,lineType:LineType,positions:list,pattern: Pattern,line_number: int):
        self.positions = positions
        self.lineType = lineType
        self.pattern = pattern
        self.line_number = line_number
        
    def getPositions(self) -> list:
        if self.lineType == LineType.HORIZONTAL:
            return [Position(self.line_number,x) for x in self.positions]
        elif self.lineType == LineType.COLUMN:
            return [Position(y,self.line_number) for y in self.positions]
        
    def getPositionsTupleList(self) -> list:
        return list(map(lambda pos: pos.toTuple(),self.getPositions()))
    
    def getLineType(self) -> LineType:
        return self.lineType
    
    def getPattern(self) -> Pattern:
        return self.pattern
    
    def __str__(self) -> str:
        return f"Positions : {self.positions} | LineType: {self.lineType.name} | Pattern: {self.pattern.getPattern()} | LineNumber : {self.line_number}"
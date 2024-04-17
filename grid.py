import enum
import numpy as np
from random import randint
from utils import ClueType, Difficulty, LineType,isLinesDifferent,NUMBER_CONVERSION,ErrorType,ErrorName
from debug import Debuger
from pattern import Pattern,Patterns,PatternType
from grid_utils import Position,PatternResultForbidden,ForbiddenPaternPosition,GridError,GridPattern
from HintWindow import HintType


class ResponsType(enum.Enum):
    CORRECT_PLAY = 0
    VALID_PLAY = 1
    UNVALID_PLAY = 2

class Line:
    
    def __init__(self,line: list, line_type: LineType = None, line_number: int = None) -> None:
        self.line = line
        self.__line_str = [str(e) for e in line]
        self.__str_line = ''.join(self.__line_str)
        self.__size = len(line)
        self.__type = line_type
        self.__line_number = line_number
        
    def changeLine(self,new_line) -> None:
        """Function that change the variable of the current object to {new_line}

        Args:
            new_line (list): line that will be stored
        """
        self.line = new_line
        self.__line_str = [str(e) for e in new_line]
        self.__str_line = ''.join(self.__line_str)

    def getEmptyPos(self) -> list:
        """Function that return a list of the position that aren't filled

        Returns:
            list: empty indexes
        """
        return [i for i,value in enumerate(self.line) if value == -1]
    
    def getFormatedLine(self) -> str:
        """Debug function that return the line in a console displayable way
        """
        return '| ' + ' | '.join(map(str,self.line)).replace("-1"," ") + ' |'
    
    def getPattern(self,pattern: Pattern) -> list:
        """Function used to detect a pattern in a line

        Args:
            patternType (GridPatternType): Type of pattern we're looking for

        Returns:
            list: list of the position that the pattern detect
            (Each pattern has positions where a certain number need a fixed value)
        """
        line = self.__str_line.replace("-1","-")
        pattern_pos = []
        last_index = 0
        if(line.find(pattern.getPattern()) == -1):
            return pattern_pos
        else:
            while ((index:=line.find(pattern.getPattern(),last_index)) != -1):
                if pattern.getType() == PatternType.GRID_PATTERN:
                    for position in pattern.getEmptyPositions():
                        if position != None:
                            pattern_pos.append(index+position)
                elif pattern.getType() == PatternType.FORBIDDEN:
                    for empty_pos in pattern.getEmptyPositions():
                        positions = [index+position for position in pattern.getPatternPositions()]
                        pattern_pos.append(PatternResultForbidden(positions,index+empty_pos,pattern.getExpectedValue()))
                elif pattern.getType() == PatternType.ERROR:
                    pos = []
                    for errorpos in pattern.getPatternPositions():
                        pos.append(errorpos+index)
                    pattern_pos.append(pos)
                last_index = index + pattern.size
        return pattern_pos
    
    def getPatternFillingPos(self,line_number: int,line_type: LineType) -> list:
        """Function that return a list of all position that can be filled with
        patterns

        Args:
            line_number (int): y coordinate
            line_type (LineType): type of line we want to get the positions from

        Returns:
            list: list of position that can be filled with known pattern
        """
        patterns = [Pattern(Patterns.OOX,PatternType.GRID_PATTERN),Pattern(Patterns.OXO,PatternType.GRID_PATTERN),Pattern(Patterns.XOO,PatternType.GRID_PATTERN),Pattern(Patterns.ZZX,PatternType.GRID_PATTERN),Pattern(Patterns.ZXZ,PatternType.GRID_PATTERN),Pattern(Patterns.XZZ,PatternType.GRID_PATTERN)]
        second_patterns = [Pattern(Patterns.OZXXX,PatternType.GRID_PATTERN),Pattern(Patterns.XXXOZ,PatternType.GRID_PATTERN),Pattern(Patterns.ZOXXX,PatternType.GRID_PATTERN),Pattern(Patterns.XXXZO,PatternType.GRID_PATTERN)]
        poses = {}
        for pattern in patterns:
            for pos in self.getPattern(pattern):
                if line_type == LineType.COLUMN:
                    poses[(pos,line_number)] = pattern.getExpectedValue()
                elif line_type == LineType.HORIZONTAL:
                    poses[(line_number,pos)] = pattern.getExpectedValue()
        if self.isAlmostFinished():
            for second_pattern in second_patterns:
                for pos in self.getPattern(second_pattern):
                    if line_type == LineType.COLUMN:
                        poses[(pos,line_number)] = second_pattern.getExpectedValue()
                    elif line_type == LineType.HORIZONTAL:
                        poses[(line_number,pos)] = pattern.getExpectedValue()
        return poses
        
    def hasMoreThanTwoOnes(self):
        """Function to detect if a line has more than two consecutive 1 that are following

        Returns:
            bool: True if has more than two 1 following False if not
        """
        return len(self.getPattern(Pattern(Patterns.OOO,PatternType.GRID_PATTERN))) != 0
    
    def hasMoreThanTwoZeros(self) -> bool:
        """Function to detects if a line has more than two consecutive 0 that are following

        Returns:
            bool: True if has more than two 0 following False if not
        """
        return len(self.getPattern(Pattern(Patterns.ZZZ,PatternType.GRID_PATTERN))) != 0
    
    def hasTooMuchOnes(self) -> bool:
        """Detect if the line has more ones than what it should (half the size
        of the line)

        Returns:
            bool: True if has too much ones False if not
        """
        return self.line.count(1) > int(self.__size/2)
    
    def hasTooMuchZeros(self) -> bool:
        """Detect if the line has more zeros than what it should (half the size
        of the line)

        Returns:
            bool: True if has too much zeros False if not
        """
        return self.line.count(0) > int(self.__size/2)
    
    def hasValidNumbers(self) -> bool:
        """Function that return if there is too much of a number in the line
        Combination of hasTooMuchOnes and hasTooMuchZeros functions
        
        Returns:
            bool: True if has too much ones/zeros False if not
        """
        ones = self.line.count(1)
        zeros = self.line.count(0)
        return False if ones > int(self.__size/2) or zeros > int(self.__size/2) else True

    def isAlmostFinished(self) -> bool:
        """Detect if a line is almost finished. That means if a line is
        one number from reaching the limit of a number
        For instance if the limit of ones is 4, return True if it has
        3 one in it.

        Returns:
            bool: True if almost finished False otherwise
        """
        return self.line.count(1) == int(self.__size/2)-1 or self.line.count(0) == int(self.__size/2)-1

    def isBorderAlreadyFill(self) -> bool:
        """Function to know if a line has already one of its border filled
        (the first cell or the last one)

        Returns:
            bool: True if has one of its border cell filled False if not
        """
        return True if self.line[0] != -1 or self.line[-1] != -1 else False

    def isFinished(self) -> bool:
        """Function that return if the function has all its cells filled or not

        Returns:
            bool: True if not empty cells False if not
        """
        return len(self.getEmptyPos()) == 0
    
    def isTwoFromFinished(self) -> bool:
        """Detect if a line has only two empty cells

        Returns:
            bool: True if has only two empty cells False if not
        """
        return self.line.count(-1) == 2
    
    def isValid(self) -> bool:
        """Function to know if the line is valid.(If no game rules
        are broken)

        Returns:
            bool: True if this line breaks no rule False if it breaks rules
        """
        isValid = True
        if self.hasMoreThanTwoOnes():
            isValid = False
        if self.hasMoreThanTwoZeros():
            isValid = False
        if self.hasTooMuchOnes():
            isValid = False
        if self.hasTooMuchZeros():
            isValid = False
        if self.hasValidNumbers() == False:
            isValid = False
        return isValid

    def testValue(self,pos,value: int):
        """Function that allow to get a new version of the line with a test value"""
        temp_line = self.line[::]
        temp_line[pos] = value
        return temp_line
    
    def getLineType(self) -> LineType:
        return self.__type
    
    def getLineNumber(self) -> int:
        return self.__line_number
    
    def getSize(self) -> int:
        return self.__size

class Grid:
    """Class used to control the grid (behind the display)
    """
    def __init__(self,size: int, difficulty: Difficulty = Difficulty.BEGINNER,gameGrid:list=[],mask:list=[]) -> None:
        self.difficulty = difficulty #Difficulty
        self.solution = []
        self.mask = mask #Grid that keeps track of filled cells
        self.styleMask = [] #Grid to apply style to certain cells
        self.gameGrid = gameGrid #Grid that keep the value of each cells
        self.getStartHealth()
        self.getStartHint()
        self.changes = 0
        
        self.debuger = Debuger()
        self.debuger.setUnactive()
        
        self.size = size
        
    def applyMaskToLine(self,line_number: int, line_type: LineType,color:int):
        """Function that apply a certain color to all the button of a 
        line or column

        Args:
            line_number (int): targeted line/column
            line_type (LineType): column or line
            color (int): number that correspond to a certain color 
            (in a list)
        """
        if line_type == LineType.HORIZONTAL:
            for x in range(self.size):
                self.styleMask[line_number][x] = color
        elif line_type == LineType.COLUMN:
            for y in range(self.size):
                self.styleMask[y][line_number] = color
                
    def applyMaskToPos(self,pos,color:int):
        """Function that apply a mask to a precise position

        Args:
            pos (_type_): targeted position
            color (int): number that correspond to a color
            present in a list
        """
        self.styleMask[pos[0]][pos[1]] = color
        
    def displayGameGrid(self):
        """Debug function to display the game grid
        """
        for line in self.gameGrid:
            print(line)
            
    def displayMaskGrid(self):
        """Debug function to display the mask grid"""
        for line in self.mask:
            print(line)
   
    def displayStyleMaskGrid(self):
        """Debug function to display style mask grid"""
        for line in self.styleMask:
            print(line) 
    
    def initializeGrids(self) -> None:
        """Function that initialise all the grids variable for this grid
        """
        self.mask = [[-1 for i in range(self.size)] for j in range(self.size)]
        self.styleMask = [[-1 for i in range(self.size)] for j in range(self.size)]
        self.gameGrid = [[-1 for i in range(self.size)] for j in range(self.size)]
        self.changes = 0
        
    def getBeginningGridFromSolution(self) -> None:
        if self.solution != []:
            self.initializeGrids()
            case_to_generate = self.getGivenStartsCellsNumber()
            i=0
            while i < (int(case_to_generate)):
                i+=1
                line_number: int = int(i%self.size) #y coord of cell to fill
                line: Line = self.getLineByInt(line_number)
                empty_pos: list = line.getEmptyPos()
                empty_poses_number = len(empty_pos)
                if empty_poses_number > 1:
                    column_number: int = empty_pos[randint(0,empty_poses_number-1)]
                    self.mask[line_number][column_number] = 1
                    self.gameGrid[line_number][column_number] = self.solution[line_number][column_number]
                            
    def getGivenStartsCellsNumber(self) -> float:
        """Function that return the number of revealed cells at the 
        begining of the game
        """
        return (self.size**2)*(self.difficulty.getPercentageShown()/100)
    
    def generateGrid(self,bonus = True) -> None:
        """Function that fill some cells in the gameGrid to help the player
        at the begining
        """
        self.initializeGrids()
        case_to_generate = (self.size**2)*0.2+1
        self.debuger.Log(f"Case to generate : {case_to_generate}")
        i = 0
        while i < (int(case_to_generate)):
            i+=1
            line_number: int = int(i%self.size) #y coord of cell to fill
            line: Line = self.getLineByInt(line_number)
            empty_pos: list = line.getEmptyPos()
            empty_poses_number = len(empty_pos)
            self.debuger.Log(f"Empty poses : {empty_poses_number}")
            if empty_poses_number > 1:
                column_number: int = empty_pos[randint(0,empty_poses_number-1)]
                self.debuger.Log(f"Column number : {column_number}")
                value = self.createValueAtPos(Position(line_number,column_number),"GENERATE") 
                if value == None:
                    i-=1
                    continue
                self.mask[line_number][column_number] = 1
                self.gameGrid[line_number][column_number] = value
                  
    def getStartHealth(self):
        """Function that initalise the vars responsible for the health
        """
        self.maxHealth = self.difficulty.getDifficultyHealth()
        self.currentHealth = self.difficulty.getDifficultyHealth()
        
    def getStartHint(self):
        """Function that initialise the vars responsible for the hints
        """
        self.maxHint = self.difficulty.getDifficultyHints()
        self.currentHint = self.difficulty.getDifficultyHints()
            
    def isLineUnique(self,line,line_number):
        """Fonction permettant de savoir si {line} est unique (pour respecter les règles)

        Args:
            line (Line): Ligne que l'on souhaite tester
            line_number (_type_): indice de la ligne que l'on test

        Returns:
            bool: True si la ligne est unique False sinon
        """
        return False if line in [line for i,line in enumerate(self.gameGrid) if i != line_number] else True
    
    def isColumnUnique(self,column, column_number):
        """Fonction permettant de savoir si {column} est unique (pour respecter les règles)

        Args:
            column (Line): Colonne que l'on souhaite tester
            column_number (_type_): indice de la colonne que l'on test

        Returns:
            bool: True si la colonne est unique False sinon
        """
        columns = [[self.gameGrid[i][j] for i in range(self.size)] for j in range(self.size)]
        return False if column in [column for i,column in enumerate(columns) if i != column_number] else True
    
    def getLineByInt(self,line_number: int) -> Line:
        """Function that return a copy of the line number {line_number}
        
        Returns:
            list: Line of the grid
        """
        return Line(self.gameGrid[line_number].copy(),LineType.HORIZONTAL,line_number)
    
    def getLines(self) -> list:
        """Function that return a list containing all the
        lines of the grid

        Returns:
            list: List of all lines
        """
        return [self.getLineByInt(i) for i in range(self.size)]
    
    def getLinesButInt(self,line_number: int) -> list:
        return [(self.getLineByInt(i),i) for i in range(self.size) if i != line_number]
    
    def getColumnByInt(self,column_number: int) ->Line:
        """Return the column corresponding to the
        {column_number}

        Args:
            column_number (int): position of the column we want to get

        Returns:
            Line: Column at positon {column_number}
        """
        return Line([line[column_number] for line in self.gameGrid].copy(),LineType.COLUMN,column_number)
    
    def getColumns(self) -> list:
        """Return the columns composing the grid

        Returns:
            list: list containing the columns
        """
        return [self.getColumnByInt(i) for i in range(self.size)]
    
    def getColumnsButInt(self,column_number:int) -> list:
        return [(self.getColumnByInt(i),i) for i in range(self.size) if i != column_number]
    
    def get(self,lineType: LineType) -> list:
        """Function that return either the columns or the lines
        depending on {lineType}
        """
        if lineType == LineType.HORIZONTAL:
            return self.getLines()
        elif lineType == LineType.COLUMN:
            return self.getColumns()
        else:
            return None

    def getStyleMaskPos(self) -> list:
        """Return a list of the positions of cells affected by the styleMask

        Returns:
            list: list of tuple
        """
        returned = []
        for y,line in enumerate(self.styleMask):
            for x,element in enumerate(line):
                if element != -1:
                    returned.append(Position(y,x))
        return returned
    
    def reinitialise(self) -> None:
        """Reset all parameter to their default value when the
        object is created
        """
        self.solution = []
        self.mask = [] #Grid that keeps track of filled cells
        self.styleMask = [] #Grid to apply style to certain cells
        self.gameGrid = [] #Grid that keep the value of each cells
        self.changes = 0
    
    def getEmptyPos(self) -> list:
        """Return a list containing all the position of cells that arent filled

        Returns:
            list[Position]: List of Position of all empty cells (not 1 or 0)
        """
        pos = []
        for y,line in enumerate(self.getLines()):
            for x in line.getEmptyPos():
                pos.append(Position(y,x))
        return pos
    
    def getEmptyCellNumber(self) -> int:
        """Return the number of cells that aren't filled"""
        return len(self.getEmptyPos())
    
    def getAlmostFinishedLines(self) -> list:
        """Return a list containing all the lines that are almost finished

        Returns:
            list: List of almost_finished line
        """
        return [(line,i) for i,line in enumerate(self.getLines()) if line.isAlmostFinished()]
    
    def getFinishedLines(self) -> list:
        return [line for line in self.getLines() if line.isFinished()]
    
    def getTwoFromFinishedLines(self) -> list:
        return [(line,i) for i,line in enumerate(self.getLines()) if line.isTwoFromFinished()]
    
    def getAlmostFinishedColumns(self) -> list:
        """Return a list containing all the columns that are almost finished

        Returns:
            list: List of almost_finished column
        """
        return [(column,i) for i,column in enumerate(self.getColumns()) if column.isAlmostFinished()]
    
    def getFinishedColumns(self) -> list:
        return [column for column in self.getColumns() if column.isFinished()]
    
    def getPositionsErrorList(self) -> list:
        positions_error = []
        #positions_pattern = []
        pattern_error = [Pattern(Patterns.OOO,PatternType.ERROR,ErrorName.THREE_ONES),Pattern(Patterns.ZZZ,PatternType.ERROR,ErrorName.THREE_ZEROS)]
        #patterns = [Pattern(Patterns.OZO,PatternType.ERROR),Pattern(Patterns.ZOZ,PatternType.ERROR),Pattern(Patterns.OOZ,PatternType.ERROR),Pattern(Patterns.ZOO,PatternType.ERROR),Pattern(Patterns.ZZO,PatternType.ERROR),Pattern(Patterns.OZZ,PatternType.ERROR)]
        for n,line in enumerate(self.getLines()):
            need_pattern_check = True
            if line.hasTooMuchOnes():
                positions_error.append(GridError(ErrorType.LINE_ERROR,ErrorName.TOO_MANY_ONES,[n],HintType.MORE_THAN_TWO_ONES))
                need_pattern_check = False
            if line.hasTooMuchZeros():
                positions_error.append(GridError(ErrorType.LINE_ERROR,ErrorName.TOO_MANY_ZEROS,[n],HintType.MORE_THAN_TWO_ZEROS))
                need_pattern_check = False
            if line.isFinished():
                if not self.isUnique(line.line,LineType.HORIZONTAL):
                    positions_error.append(GridError(ErrorType.LINE_ERROR,ErrorName.LINE_SIMILAR,[n],HintType.COMPARING))
            if need_pattern_check:
                for pattern in pattern_error:
                    for pos in line.getPattern(pattern):
                        pos_list = list(zip([n for i in range(len(pos))],pos))
                        if pattern.getPattern() == Patterns.ZZZ.getPatternString():
                            positions_error.append(GridError(ErrorType.PATTERN_ERROR,pattern.getError(),pos_list,HintType.TOO_MUCH_ZEROS))
                        elif pattern.getPattern() == Patterns.OOO.getPatternString():
                            positions_error.append(GridError(ErrorType.PATTERN_ERROR,pattern.getError(),pos_list,HintType.TOO_MUCH_ONES))
        for j,column in enumerate(self.getColumns()):
            need_pattern_check = True
            if column.hasTooMuchOnes():
                positions_error.append(GridError(ErrorType.COLUMN_ERROR,ErrorName.TOO_MANY_ONES,[j],HintType.MORE_THAN_TWO_ONES))
                need_pattern_check = False
            if column.hasTooMuchZeros():
                positions_error.append(GridError(ErrorType.COLUMN_ERROR,ErrorName.TOO_MANY_ZEROS,[j],HintType.MORE_THAN_TWO_ZEROS))
                need_pattern_check = False
            if column.isFinished():
                if not self.isUnique(column.line,LineType.COLUMN):
                    positions_error.append(GridError(ErrorType.COLUMN_ERROR,ErrorName.COLUMN_SIMILAR,[j],HintType.COMPARING))
            if need_pattern_check:
                for pattern in pattern_error:
                    for pos in column.getPattern(pattern):
                        pos_list = list(zip(pos,[j for i in range(len(pos))]))
                        if pattern.getPattern() == Patterns.ZZZ.getPatternString():
                            positions_error.append(GridError(ErrorType.PATTERN_ERROR,pattern.getError(),pos_list,HintType.TOO_MUCH_ZEROS))
                        elif pattern.getPattern() == Patterns.OOO.getPatternString():
                            positions_error.append(GridError(ErrorType.PATTERN_ERROR,pattern.getError(),pos_list,HintType.TOO_MUCH_ONES)) 
        return positions_error
    
    def getValidPositionsPattern(self) -> list:
        position_pattern = []
        patterns = [Pattern(Patterns.OZO,PatternType.ERROR),Pattern(Patterns.ZOZ,PatternType.ERROR),Pattern(Patterns.OOZ,PatternType.ERROR),Pattern(Patterns.ZOO,PatternType.ERROR),Pattern(Patterns.ZZO,PatternType.ERROR),Pattern(Patterns.OZZ,PatternType.ERROR)]
        for i,line in enumerate(self.getLines()):
            for pattern in patterns:
                for positions in line.getPattern(pattern):
                    position_pattern.append(GridPattern(LineType.HORIZONTAL,positions,pattern,i))
        for j,column in enumerate(self.getColumns()):
            for pattern in patterns:
                for positions in column.getPattern(pattern):
                    position_pattern.append(GridPattern(LineType.COLUMN,positions,pattern,j))
        return position_pattern

    def getTwoFromFinishedColumns(self) -> list:
        return [(column,i) for i,column in enumerate(self.getColumns()) if column.isTwoFromFinished()]
    
    def isPosInMask(self,pos) -> bool:
        return self.mask[pos[0]][pos[1]] != -1
    
    def isUnique(self,line: list,lineType: LineType) -> bool:
        """Function tha return if {line} is present only once in the grid
        which mean that it is unique

        Args:
            line (list): line to test
            lineType (LineType): if it is a line or a column

        Returns:
            bool: True if unique False if not
        """
        result = []
        if lineType == LineType.COLUMN:
            columns = self.getColumns()
            result = [isLinesDifferent(line,column.line) for column in columns] 
        elif lineType == LineType.HORIZONTAL:
            lines = self.getLines()
            result = [isLinesDifferent(line,l.line) for l in lines]
        return result.count(False) <= 1
            
    def setGrid(self,grid: list,mask: list) -> None:
        self.gameGrid = grid   
        self.mask = mask
        
    def setSolutionGrid(self,solution:list) -> None:
        self.solution = solution
    
    def reinitialiseStyleMask(self) -> None:
        """Function to reinitialise the styleMaskGrid
        """
        self.styleMask = [[-1 for i in range(self.size)] for j in range(self.size)]
    
    def createValueAtPos(self,pos: Position,step = "SOLVING") -> int:
        """Use for grid generation to generate a value that respect
        the rules of the game
        
        step -> "GENERATE" or "SOLVE"
        
        Args:
            pos (tuple) : (pos[0]: line_number(y) pos[1]:column_number (x))
        """
        value = randint(1,1) #A random value is generated
        line = self.getLineByInt(pos.getLineNumber())
        column = self.getColumnByInt(pos.getColumnNumber())
        self.debuger.Log(f"Line : {line.line}")
        self.debuger.Log(f"Column : {column.line}")
        self.debuger.Log(f"Value : {value}")
        a = line.getPatternFillingPos(pos.getLineNumber(),LineType.HORIZONTAL)
        b = column.getPatternFillingPos(pos.getColumnNumber(),LineType.COLUMN)
        pos_pattern_dict = {**a,**b}
        self.debuger.Log(f"Pattern dictionnary : {pos_pattern_dict}")
        if pos_pattern_dict.get(pos.toTuple()) != None:
            return pos_pattern_dict[pos.toTuple()]
        else:
            if step == "GENERATE":
                if line.isBorderAlreadyFill() and (pos.x == self.size-1 or pos.x == 0):
                    self.debuger.Log(f"Info : {line.isBorderAlreadyFill()}")
                    return None
                elif column.isBorderAlreadyFill() and (pos.y == self.size-1 or pos.y == 0):
                    self.debuger.Log(f"Info : {column.isBorderAlreadyFill()}")
                    return None
            temp_line = line.line[:]
            temp_column = column.line[:]
            temp_line[pos.x] = value
            temp_column[pos.y] = value
            temp_line = Line(temp_line)
            temp_column = Line(temp_column)
            self.debuger.Log(f"Potential Result Line : {temp_line.line}")
            self.debuger.Log(f"Potential Result Column : {temp_column.line}")
            forbidden_pattern_dict = {}
            forbidden_pattern_pos = []
            #Code responsible to prevent those situations
            #00
            #--1
            #--1
            pattern_list = [Pattern(Patterns.OOX,PatternType.FORBIDDEN),Pattern(Patterns.OXO,PatternType.FORBIDDEN),Pattern(Patterns.XOO,PatternType.FORBIDDEN),Pattern(Patterns.XZZ,PatternType.FORBIDDEN),Pattern(Patterns.ZXZ,PatternType.FORBIDDEN),Pattern(Patterns.ZZX,PatternType.FORBIDDEN)]
            for pattern in pattern_list:
                self.debuger.Log(f"Pattern : {pattern.getPattern()}")
                for line_pattern_result in temp_line.getPattern(pattern):
                    self.debuger.Log(f"Line pattern result : {line_pattern_result}")
                    temp_pos = Position(pos.y,line_pattern_result.empty_position)
                    forbidden_pattern_pos.append(ForbiddenPaternPosition(temp_pos,line_pattern_result,LineType.HORIZONTAL))
                    #forbidden_pattern_pos.append([x[0],x[2],temp_pos,LineType.HORIZONTAL])
                    forbidden_pattern_dict.setdefault(temp_pos.toTuple(),[]).append(line_pattern_result.getExpectedValue())
                for column_pattern_result in temp_column.getPattern(pattern):
                    self.debuger.Log(f"Column pattern result : {column_pattern_result}")
                    temp_pos = Position(pos.x,column_pattern_result.empty_position)
                    forbidden_pattern_pos.append(ForbiddenPaternPosition(temp_pos,column_pattern_result,LineType.COLUMN))
                    #forbidden_pattern_pos.append([y[0],y[2],t,LineType.COLUMN])
                    forbidden_pattern_dict.setdefault(temp_pos.toTuple(),[]).append(column_pattern_result.getExpectedValue())
            self.debuger.Log(f"forbidden pattern dict : {forbidden_pattern_dict}")
            for key in forbidden_pattern_dict.keys():
                self.debuger.Log(f"{key} | length : {len(set(forbidden_pattern_dict[key]))}")
                if len(set(forbidden_pattern_dict[key])) == 2:
                    self.debuger.Log(f"Wrong value guessed -> changed to {NUMBER_CONVERSION[value]}")
                    return NUMBER_CONVERSION[value]
            self.debuger.Log(f"forbidden poses : {forbidden_pattern_pos}")
            unvalid_line_count = 0
            #Code that check for the new line and column create by the previous pattern
            for forbidden_pos in forbidden_pattern_pos:
                if forbidden_pos.getLineType() == LineType.COLUMN:
                    if pos.getColumnNumber() in forbidden_pos.getPositions():
                        l = self.getLineByInt(forbidden_pos.getLineNumber())
                        l.line[forbidden_pos.y] = forbidden_pos.getExpectedValue()
                        l.changeLine(l.line)
                        self.debuger.Log(f"Changes second line : {l.line}")
                        if l.isValid() == False:
                            unvalid_line_count += 1
                elif forbidden_pos.getLineType() == LineType.HORIZONTAL:
                    if pos.getColumnNumber() in forbidden_pos.getPositions():
                        l = self.getColumnByInt(forbidden_pos.getColumnNumber())
                        l.line[forbidden_pos.x] = forbidden_pos.getExpectedValue()
                        l.changeLine(l.line)
                        self.debuger.Log(f"Changes second column : {l.line}")
                        if l.isValid() == False:
                            unvalid_line_count += 1
            return value if unvalid_line_count == 0 else NUMBER_CONVERSION[value]
        
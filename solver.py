from grid import Grid,Line
from utils import LineType,NUMBER_CONVERSION,isLinesDifferent
from debug import Debuger
from pattern import Pattern,Patterns,PatternType
from grid_utils import Entry
    
class Solver:
    """Class responsible to solve the grid it gets as parameter
    """
    
    def __init__(self,grid: Grid = False) -> None:
        self.current_step: int = 0 #current step in the solving process (used for the step_dict)
        self.current_displayed_step: int = -1 #current grid step displayed in the solving menu of the game
        self.max_steps: int = 0 
        self.grid = grid #grid object that need to be solved
        self.basic_grid : list = [line for line in self.grid.getLines()] #state of the grid before it has been solved
        self.step_dict = {} #dictionnary that store every entry added in the grid
        
        self.debug = Debuger()
        self.debug.setUnactive()
        
        self.steps_list = [] #list that store the grid at the end of a solving process
        self.last_grid = [l[:] for l in self.grid.gameGrid]
        
        self.first_check_patterns = [Pattern(Patterns.ZZX,PatternType.GRID_PATTERN),Pattern(Patterns.XZZ,PatternType.GRID_PATTERN),Pattern(Patterns.OOX,PatternType.GRID_PATTERN),Pattern(Patterns.XOO,PatternType.GRID_PATTERN)] 
        self.second_check_patterns = [Pattern(Patterns.OXO,PatternType.GRID_PATTERN),Pattern(Patterns.ZXZ,PatternType.GRID_PATTERN)]
        self.almost_finished_patterns = [Pattern(Patterns.ZOXXX,PatternType.GRID_PATTERN),Pattern(Patterns.OZXXX,PatternType.GRID_PATTERN),Pattern(Patterns.XXXOZ,PatternType.GRID_PATTERN),Pattern(Patterns.XXXZO,PatternType.GRID_PATTERN)]
        
    def applyChanges(self,entries: list) -> None:
        """Function that takes all the entry stored in the step_dict and 
        change the grid correspondingly"""
        for entry in entries:
            if entry.getValue() != None:
                self.grid.gameGrid[entry.y][entry.x] = entry.getValue() 
                 
    def addStepEntry(self,step: int,entry: Entry) -> None:
        """
        step_dict -> {0:[Entry1,Entry2,...]}
        Entry -> x,y,value
        """
        self.step_dict[step].append(entry)
              
    def backTrack(self) -> bool:
        """Function that apply the backtrack algorithm to the grid to solve it
        It tests all possible value to each empty cells and verify if by doing
        so, the constraints are still respected.
        If it is, then we can solve the next empty cell, if it is not, then we go back
        from 1 cell and try to change its value to see if it solve the next one.
        We can go back indefinitely if needed until all cells are solved

        Returns:
            bool: True if the cell filled respect the rules False if not
        """
        if self.grid.getEmptyCellNumber() == 0:
            return True
        else:
            pos = self.grid.getEmptyPos()[0] #y #x
            original_line = self.grid.getLineByInt(pos.getLineNumber())
            
            for value in [0,1]:
                temp_line = self.grid.getLineByInt(pos.getLineNumber())
                temp_column = self.grid.getColumnByInt(pos.getColumnNumber())
                temp_line.line[pos.x] = value
                temp_column.line[pos.y] = value
                temp_line.changeLine(temp_line.line)
                temp_column.changeLine(temp_column.line)
                if len(temp_line.getPattern(Pattern(Patterns.OOO,PatternType.GRID_PATTERN))) == 0 and len(temp_line.getPattern(Pattern(Patterns.ZZZ,PatternType.GRID_PATTERN))) == 0 and len(temp_column.getPattern(Pattern(Patterns.OOO,PatternType.GRID_PATTERN))) == 0 and len(temp_column.getPattern(Pattern(Patterns.ZZZ,PatternType.GRID_PATTERN))) == 0:
                    if temp_line.hasValidNumbers() == True and temp_column.hasValidNumbers() == True:
                        is_line_unique = not False in [isLinesDifferent(temp_line.line,line.line) for line in self.grid.getLines()]
                        is_column_unique = not False in [isLinesDifferent(temp_column.line,column.line) for column in self.grid.getColumns()]
                        if is_line_unique == True and is_column_unique == True:
                            self.grid.gameGrid[pos.getLineNumber()] = temp_line.line
                            self.addStepEntry(self.current_step,Entry(pos.x,pos.y,value))
                            self.nextStep()
                            if(self.backTrack()):
                                return True
                            
                            self.grid.gameGrid[pos.getLineNumber()] = original_line.line
                            self.addStepEntry(self.current_step,Entry(pos.x,pos.y,None))
                            self.nextStep()
            return False
        
    def computeMaxStep(self) -> None:
        """Function that calculate the maximum number of step needed to solve the grid
        """
        self.max_steps = list(self.step_dict.keys())[-1] 
       
    def displayBasicGrid(self) -> None:
        """Debug function that display the original grid (start grid)"""
        print("-"*30)
        for line in self.basic_grid:
            print(line.getFormatedLine())
            
    def displayGrid(self) -> None:
        """Debug function that display the grid in a readable way
        """
        print("-"*30)
        for line in self.grid.getLines():
            print(line.getFormatedLine())
       
    def displayStepDict(self,step: int = None) -> None:
        """Debug funciton used to display each step of the step_dict
        It can also display a specified step
        """
        for k in self.step_dict.keys():
            if step != None:
                if k == step:
                    print(f"========== STEP {k} ==========")
                    for entry in self.step_dict[k]:
                        print(f"- {entry.toTuple()} -> {entry.getValue()}")
            else:
                print(f"========== STEP {k} ==========")
                for entry in self.step_dict[k]:
                    print(f"- {entry.toTuple()} -> {entry.getValue()}")
          
    def fillLine(self,lines,lineType: LineType) -> None:
        """Function that tests if a line already has the correct number of 1 or 0
        and fill the remaining cells by the other values (based on the game rules)
        
        Args:
            lines (list[Line]): list containing the lines of the game
        """
        for i,line in enumerate(lines):
            counts = {k:line.line.count(k) for k in [0,1]} #dictionnary that contain the count of each value for the line
            full_value = max(counts,key=lambda x: counts[x]) #wich value is the most present in the line
            if line.line.count(full_value) == int(self.grid.size/2): #if it is equal to half the size of the line
                for pos in line.getEmptyPos(): #get all the empty cells that should be filled by the other value
                    if lineType == LineType.HORIZONTAL: #if the line is horizontal
                        self.addStepEntry(self.current_step,Entry(pos,i,NUMBER_CONVERSION[full_value]))
                    elif lineType == LineType.COLUMN: #if it is a column
                        self.addStepEntry(self.current_step,Entry(i,pos,NUMBER_CONVERSION[full_value]))
           
    def getCurrentDisplayedStep(self) -> int:
        """Return the step currently displayed in the window"""
        return self.current_displayed_step
    
    def getCurrentStep(self) -> int:
        """Return the current step of solving"""
        return self.current_step
    
    def getMaxStep(self) -> int:
        """Return the total number of steps needed to solve the grid"""
        return self.max_steps
    
    def getSolvableGrid(self) -> list:
        """Function that continuously generates grid until it is solvable

        Returns:
            (gameGrid,maskGrid): Start grid that is solvable at the end with its
            mask grid
        """
        self.current_grid = [line[:] for line in self.grid.gameGrid]
        self.current_mask_grid = [line[:] for line in self.grid.mask]
        self.solve()
        self.backTrack()
        while(self.isSolvable() == False):
            self.reinitialize()
            self.grid.generateGrid()
            self.solve()
            self.backTrack()
        return [line.line for line in self.grid.getLines()]
       
    def isGridDifferent(self,grid1: list,grid2: list) -> bool:
        """Function that test if 2 gameGrid are similar or not

        Args:
            grid1 (list): first gridGame
            grid2 (list): second gridGame

        Returns:
            bool: True if they are different false if they are similar
        """
        total = 0 #sum of each grid lines
        for t in zip(grid1,grid2): #creation of tuple containing the same line from both grid (ex: both first line, etc...)
            for t2 in zip(t[0],t[1]): #creation of a tuple for each value of each line
                total += (t2[0]-t2[1]) #if they are similare, then substracting them should give 0
        return total != 0 #if all the line are the same the sum should be 0
        
    def isSolvable(self) -> bool:
        """Function used to know if the grid is solvable or not.
        Check all unvalid pattern and if detected, it means the grid
        is not solvable (by the actual solver)

        Returns:
            bool: True if solvable False if not
        """
        solvable = True
        for j,lines in enumerate([self.grid.getLines(),self.grid.getColumns()]):
            for i,line in enumerate(lines):
                if line.hasMoreThanTwoOnes(): #111 pattern
                    solvable = False
                    self.debug.Log(f"Unsolvable three ones follow #{i}")
                if line.hasMoreThanTwoZeros(): #000 pattern
                    solvable = False
                    self.debug.Log(f"Unsolvable three zeros follow #{i}")
                if line.hasTooMuchOnes(): #if line/column has more ones than half the size of the grid
                    solvable = False
                    self.debug.Log(f"Unsolvable too many ones #{i}")
                if line.hasTooMuchZeros(): #if line/column has more zeros than half the size of the grid
                    solvable = False
                    self.debug.Log(f"Unsolvable too many zeros #{i}")
                if j == 0:
                    if not self.grid.isUnique(line.line,LineType.HORIZONTAL): #if multiple lines are the same
                        solvable = False
                        self.debug.Log(f"Unsolvable line not unique #{i}")
                elif j == 1:
                    if not self.grid.isUnique(line.line,LineType.COLUMN): #if multiple columns are the same
                        solvable = False
                        self.debug.Log(f"Unsolvable column not unique #{i}")
                if self.grid.getEmptyCellNumber() != 0: #if the solver left unfilled cells
                    solvable = False
                    self.debug.Log(f"Unsolvable grid not filled")
        return solvable
                  
    def nextDisplayedStep(self) -> None:
        """Add 1 to displayed step"""
        self.current_displayed_step = self.current_displayed_step + 1 if self.current_displayed_step < self.max_steps else self.current_displayed_step
        
    def nextStep(self) -> None:
        """Add 1 to current step and update the step_dict"""
        self.current_step = self.current_step + 1
        self.step_dict[self.current_step] = []
    
    def previousDisplayedStep(self) -> None:
        """go back from 1 displayed step"""
        self.current_displayed_step = self.current_displayed_step - 1 if self.current_displayed_step < self.max_steps else self.current_displayed_step
    
    def previousStep(self) -> None:
        """Go back from 1 step"""
        self.current_step = self.current_step - 1 if self.current_step > 0 else self.current_step
      
    def setGrid(self,grid: Grid) -> None:
        """Function that allow to change the grid the solver is in charge to solve"""
        self.reinitialize()
        self.grid = grid
        
    def solve(self) -> None:
        """Function that solve the pattern present in the grid to
        make the backtracking algorithm faster
        """
        self.step_dict[self.current_step] = []
        while self.grid.getEmptyCellNumber() != 0: #as long as the grid is not filled
            for i,check in enumerate([self.first_check_patterns,self.second_check_patterns]): #check for the first importants moves
                lines = self.grid.getLines() #get all the lines
                self.solveLine(lines,check,LineType.HORIZONTAL) #solve them by searching if a pattern is found in them
                columns = self.grid.getColumns()
                self.solveLine(columns,check,LineType.COLUMN)
            self.applyChanges(self.step_dict[self.current_step])
            self.nextStep()
            for j,lineType in enumerate([LineType.HORIZONTAL,LineType.COLUMN]):
                lines = self.grid.get(lineType)
                if lines != None:
                    self.fillLine(lines,lineType)
                    self.applyChanges(self.step_dict[self.current_step])
            self.nextStep() 
            if not self.isGridDifferent(self.last_grid,self.grid.gameGrid):
                break
            self.last_grid = [l[:] for l in self.grid.gameGrid]
        self.computeMaxStep()  
        
    def solveLine(self,lines,patterns: list,line_type: LineType) -> None:
        """Function that get a list of Lines and a pattern and try to solve
        the pattern for each of these line

        Args:
            lines (List[Line]): list of Line
            patterns (list): list of pattern to test
            line_type (LineType): HORIZONTAL or COLUMN
        """
        for i,line in enumerate(lines):
            for pattern in patterns:
                if isinstance(line,tuple):
                    for pos in line[0].getPattern(pattern):
                        if line_type == LineType.HORIZONTAL:
                            self.addStepEntry(self.current_step,Entry(pos,line[1],pattern.getExpectedValue()))
                        elif line_type == LineType.COLUMN:
                            self.addStepEntry(self.current_step,Entry(line[1],pos,pattern.getExpectedValue()))
                if isinstance(line,Line):
                    for pos in line.getPattern(pattern):
                        if line_type == LineType.HORIZONTAL:
                            self.addStepEntry(self.current_step,Entry(pos,i,pattern.getExpectedValue()))
                        elif line_type == LineType.COLUMN:
                            self.addStepEntry(self.current_step,Entry(i,pos,pattern.getExpectedValue()))        
        
    def reinitialize(self) -> None:
        """Reset all parameter of the class as if it the object has just
        been created
        """
        self.step_dict = {}
        self.current_step = 0
        self.current_displayed_step = -1
        self.max_steps = 0
        
        self.steps_list = [] #list that store the grid at the end of a solving process
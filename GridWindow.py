from PyQt5.QtWidgets import QGridLayout,QWidget,QLabel
from PyQt5.QtCore import Qt

import string

from grid import Grid
from customWidget import GameButton
from utils import Difficulty,GameButtonType,ButtonState,getCssFile,STRING_CONVERSION,ErrorType,LineType
from config import WIDTH
from solver import Solver
from debug import Debuger
from grid_utils import Entry,Position,GridPattern
from pattern import Pattern,Patterns

class GridWidget(QWidget):
    """Widget use as a template for all the grid generated in the game
    It is mostly used for the display part"""
    def __init__(self,size: int, difficulty: Difficulty, gameGrid: list = [], mask: list = []) -> None:
        super().__init__()
        
        self.setStyleSheet("background-color: #c8d6e5;")
        
        self.size = size #Number of row/column
        self.difficulty = difficulty #Difficulty
        
        self.grid = Grid(size,difficulty,gameGrid,mask)
        
        self.debuger = Debuger()
        self.debuger.setUnactive()

        self.styleMaskPos = []
        self.styleMaskActivated = False
        
        self.Alphabet = list(string.ascii_uppercase)
        
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(20,20,20,20)
        self.layout.setSpacing(20)
        
        self.buttons = [[None for i in range(self.size)] for j in range(self.size)]
        
    def applyStyleMask(self):
        self.styleMaskActivated = True
        self.styleMaskPos = self.grid.getStyleMaskPos()
        for pos in self.styleMaskPos:
            color_pos = int(self.grid.styleMask[pos.y][pos.x]%len(GameButtonType.getDeactivatedButtonColorList()))
            if self.buttons[pos.y][pos.x].getState() == ButtonState.DEACTIVATED:
                self.buttons[pos.y][pos.x].setTemporaryButtonType(GameButtonType.getDeactivatedButtonColorList()[color_pos])
            else:
                self.buttons[pos.y][pos.x].setTemporaryButtonType(GameButtonType.getActivatedButtonColorList()[color_pos])
            
    def revokeStyleMask(self):
        self.styleMaskActivated = False
        for pos in self.grid.getStyleMaskPos():
            if self.buttons[pos.y][pos.x].getState() == ButtonState.DEACTIVATED:
                self.buttons[pos.y][pos.x].setTemporaryButtonType(GameButtonType.DISABLED)
            elif self.buttons[pos.y][pos.x].getState() == ButtonState.SELECTED:
                self.buttons[pos.y][pos.x].setTemporaryButtonType(GameButtonType.SELECTED)
            else:
                self.buttons[pos.y][pos.x].setTemporaryButtonType(GameButtonType.UNFILLED)
        self.grid.reinitialiseStyleMask()
        
    def initDisplay(self,hasNumber: bool = False) -> None:
        self.button_size = int(((WIDTH/2)-100)/self.size)
        if hasNumber:
            for i in range(1,self.size+1):
                numberLabel = QLabel(str(i))
                numberLabel.setAlignment(Qt.AlignCenter)
                numberLabel.setStyleSheet("""
                                        color: white;
                                        padding: 0px 0px;
                                        margin-bottom: 0px;
                                        margin-top: 0px;
                                        background-color: none;
                                        border: none;
                                        font-size: 20px;
                                            """)
                letterLabel = QLabel(self.Alphabet[i-1])
                letterLabel.setAlignment(Qt.AlignCenter)
                letterLabel.setStyleSheet("""
                                        color: white;
                                        padding: 0px 0px;
                                        margin-bottom: 0px;
                                        margin-top: 0px;
                                        background-color: none;
                                        border: none;
                                        font-size: 20px;
                                            """)
                self.layout.addWidget(numberLabel,0,i)
                self.layout.addWidget(letterLabel,i,0)
        for i,line in enumerate(self.grid.mask):
            for j,element in enumerate(line):
                self.buttons[i][j] = GameButton(GameButtonType.UNFILLED,ButtonState.EMPTY)
                self.buttons[i][j].setFixedHeight(self.button_size)
                self.buttons[i][j].setFixedWidth(self.button_size)
                if element == 1:
                    self.buttons[i][j].setText(f"{self.grid.gameGrid[i][j]}")
                    self.buttons[i][j].setDisabled(True)
                    self.buttons[i][j].buttonType = GameButtonType.DISABLED
                    self.buttons[i][j].setState(ButtonState.DEACTIVATED)
                self.buttons[i][j].updateStyleSheet()
                self.layout.addWidget(self.buttons[i][j],i+1,j+1)
                
    def connectAllButtons(self,func) -> None:
        """Function use to connect all the button of the grid to a function
        that will be executed when pressed"""
        for i,line in enumerate(self.buttons):
            for j in range(len(line)):
                self.buttons[i][j].connect(lambda _,x=i,y=j:func(x,y))
                
    def changeColor(self,i,j):
        if self.styleMaskActivated:
            self.revokeStyleMask()
        if self.buttons[i][j].state != ButtonState.DEACTIVATED:
            self.buttons[i][j].setTemporaryButtonType(GameButtonType.SELECTED)
            self.buttons[i][j].setState(ButtonState.SELECTED)
            if self.buttons[i][j].text() == "":
                self.buttons[i][j].setText("0")
            elif self.buttons[i][j].text() == "0":
                self.buttons[i][j].setText("1")
            elif self.buttons[i][j].text() == "1":
                self.buttons[i][j].setText("")
            
    def getSelectedButton(self) -> list:
        selected = []
        for i,line in enumerate(self.buttons):
            for j,button in enumerate(line):
                if button.getState() == ButtonState.SELECTED:
                    selected.append(Entry(j,i,STRING_CONVERSION[button.text()]))
                    self.debuger.Log(f"y:{i},x:{j} -> state: {button.getState().toString()}")
        return selected
    
    def getSelectedGrid(self) -> Grid:
        """Return a grid object with the values selected in the grid"""
        gameGridCopy = [self.grid.getLineByInt(i).line for i in range(self.size)]
        maskGridCopy = [list(self.grid.mask[i].copy()) for i in range(self.size)]
        temp_grid = Grid(self.size,self.difficulty,gameGridCopy,maskGridCopy)
        for entry in self.getSelectedButton():
            temp_grid.gameGrid[entry.y][entry.x] = entry.getValue()
        return temp_grid
           
    def resetGrid(self):
        """Function that reset the display of the grid
        """
        for i,line in enumerate(self.grid.mask):
            for j,element in enumerate(line):
                self.buttons[i][j].buttonType = GameButtonType.UNFILLED
                self.buttons[i][j].setState(ButtonState.EMPTY)
                self.buttons[i][j].setText("")
                self.buttons[i][j].setDisabled(False)
                self.buttons[i][j].setFixedHeight(self.button_size)
                self.buttons[i][j].setFixedWidth(self.button_size)
                if element == 1:
                    self.buttons[i][j].buttonType = GameButtonType.DISABLED
                    self.buttons[i][j].setState(ButtonState.DEACTIVATED)
                    self.buttons[i][j].setText(f"{self.grid.gameGrid[i][j]}")
                    self.buttons[i][j].setDisabled(True)
                    self.buttons[i][j].setFixedHeight(self.button_size)
                    self.buttons[i][j].setFixedWidth(self.button_size)
                self.buttons[i][j].updateStyleSheet()
           
    def changeDifficulty(self,difficulty: Difficulty):
        self.grid = Grid(self.size,difficulty)  
        self.grid.generateGrid() 
        solver = Solver(self.grid)
        solvable_grid = solver.getSolvableGrid()
        self.grid.setSolutionGrid(solvable_grid)
        self.grid.getBeginningGridFromSolution()
        self.grid.getStartHealth()
        self.grid.getStartHint()
        self.resetGrid()  
        
    def checkGrid(self) -> None:
        #selected_pos = self.getSelectedButton() #List of {Entry} corresponding to the selected cells
        selectedGrid = self.getSelectedGrid()
        position_error = selectedGrid.getPositionsErrorList()
        for c,error in enumerate(position_error):
            if error.getType() == ErrorType.LINE_ERROR:
                self.grid.applyMaskToLine(error.getPositions()[0],LineType.HORIZONTAL,c)
            elif error.getType() == ErrorType.COLUMN_ERROR:
                self.grid.applyMaskToLine(error.getPositions()[0],LineType.COLUMN,c)
            elif error.getType() == ErrorType.PATTERN_ERROR:
                for pos in error.getPositions():
                    self.grid.applyMaskToPos(pos,c)
        self.applyStyleMask()
        return position_error
        
    def getSelectedPattern(self) -> list:
        selected_pos = self.getSelectedButton()
        selected_grid = self.getSelectedGrid()
        valid_positions = selected_grid.getValidPositionsPattern()
        selected_pattern = []
        for entry in selected_pos:
            for grid_pattern in valid_positions:
                for pos in grid_pattern.getPositions():
                    if entry.toTuple() == pos.toTuple():
                        selected_pattern.append(grid_pattern)
        return selected_pattern
    
    def getColorableCells(self) -> list:
        colorable = []
        for y in range(self.size):
            for x in range(self.size):
                if self.grid.gameGrid[y][x] != -1 and self.grid.mask[y][x] == -1:
                    colorable.append(Entry(x,y,self.grid.gameGrid[y][x]))
        return colorable
    
    def colorGrid(self) -> None:
        selected_pattern = self.getSelectedPattern()
        selected_grid = self.getSelectedGrid()
        mask_added = 1
        while mask_added != 0:
            mask_added = 0
            for pos in self.getColorableCells() + self.getSelectedButton():
                if selected_grid.gameGrid[pos.y][pos.x] != -1:
                    def_valid = False
                    valid = False
                    for grid_pattern in selected_pattern:
                        if pos.toTuple() in grid_pattern.getPositionsTupleList():
                            if grid_pattern.getPattern().getPattern() in [Patterns.ZOZ.getPatternString(),Patterns.OZO.getPatternString()]:
                                valid_cell_number = 0
                                for position in grid_pattern.getPositions():
                                    valid_cell_number += 1 if self.grid.mask[position.y][position.x] != -1 else 0
                                if grid_pattern.getLineType() == LineType.HORIZONTAL:
                                    if pos.x == grid_pattern.positions[1] and valid_cell_number == 2:
                                        def_valid = True
                                    else:
                                        valid = True
                                elif grid_pattern.getLineType() == LineType.COLUMN:
                                    if pos.y == grid_pattern.positions[1] and valid_cell_number == 2:
                                        def_valid = True
                                    else:
                                        valid = True
                            if grid_pattern.getPattern().getPattern() in [Patterns.OOZ.getPatternString(),Patterns.ZOO.getPatternString(),Patterns.ZZO.getPatternString(),Patterns.OZZ.getPatternString()]:
                                valid_cell_number = 0
                                for position in grid_pattern.getPositions():
                                    valid_cell_number += 1 if self.grid.mask[position.y][position.x] != -1 else 0
                                if grid_pattern.getLineType() == LineType.HORIZONTAL:
                                    if (pos.x == grid_pattern.positions[0] or pos.x == grid_pattern.positions[2]) and valid_cell_number == 2 and grid_pattern.getPattern().getMaximumValue() != pos.getValue():
                                        def_valid = True
                                    else:
                                        valid = True
                                elif grid_pattern.getLineType() == LineType.COLUMN:
                                    if (pos.y == grid_pattern.positions[0] or pos.y == grid_pattern.positions[2]) and valid_cell_number == 2 and grid_pattern.getPattern().getMaximumValue() != pos.getValue():
                                        def_valid = True
                                    else:
                                        valid = True
                        for line in selected_grid.getFinishedLines():
                            valid_cell_number = 0
                            valid_one = 0
                            valid_zero = 0
                            for x in range(selected_grid.size):
                                valid_cell_number += 1 if selected_grid.mask[line.getLineNumber()][x] != -1 else 0
                                valid_one += 1 if selected_grid.mask[line.getLineNumber()][x] != -1 and selected_grid.gameGrid[line.getLineNumber()][x] == 1 else 0
                                valid_zero += 1 if selected_grid.mask[line.getLineNumber()][x] != -1 and selected_grid.gameGrid[line.getLineNumber()][x] == 0 else 0
                            if pos.getLineNumber() == line.getLineNumber() and valid_cell_number == selected_grid.size - 1:
                                def_valid = True
                            elif pos.getLineNumber() == line.getLineNumber() and (valid_one == int(self.size/2) or valid_zero == int(self.size/2)):
                                def_valid = True
                            else:
                                valid = True
                        for column in selected_grid.getFinishedColumns():
                            valid_cell_number = 0
                            valid_one = 0
                            valid_zero = 0
                            for y in range(selected_grid.size):
                                valid_cell_number += 1 if selected_grid.mask[y][column.getLineNumber()] != -1 else 0
                                valid_one += 1 if selected_grid.mask[y][column.getLineNumber()] != -1 and selected_grid.gameGrid[y][column.getLineNumber()] == 1 else 0
                                valid_zero += 1 if selected_grid.mask[y][column.getLineNumber()] != -1 and selected_grid.gameGrid[y][column.getLineNumber()] == 0 else 0
                            if pos.getColumnNumber() == column.getLineNumber() and valid_cell_number == selected_grid.size - 1:
                                def_valid = True
                            elif pos.getLineNumber() == column.getLineNumber() and (valid_one == int(self.size/2) or valid_zero == int(self.size/2)):
                                def_valid = True
                            else:
                                valid = True
                        if not pos.getValue() == None:
                            if def_valid:
                                self.grid.gameGrid[pos.y][pos.x] = pos.getValue()
                                self.grid.mask[pos.y][pos.x] = 1
                                mask_added += 1
                                self.buttons[pos.y][pos.x].setTemporaryButtonType(GameButtonType.CORRECT)
                                self.buttons[pos.y][pos.x].setState(ButtonState.FILLED)
                            elif valid:
                                self.grid.gameGrid[pos.y][pos.x] = pos.getValue()
                                self.buttons[pos.y][pos.x].setTemporaryButtonType(GameButtonType.VALID)
                                self.buttons[pos.y][pos.x].setState(ButtonState.FILLED_VALID)
                selected_grid = self.getSelectedGrid()
            
class Grid4x4(GridWidget):
    
    def __init__(self,difficulty:Difficulty=Difficulty.BEGINNER,gameGrid:list=[],mask:list=[]):
        super().__init__(4,difficulty,gameGrid,mask)
        
        self.grid.generateGrid(False)
        
        self.initDisplay(True)
        self.connectAllButtons(self.click)

    def click(self,i,j):
        self.changeColor(i,j)
    
class Grid6x6(GridWidget):
    
    def __init__(self,difficulty:Difficulty=Difficulty.BEGINNER,gameGrid:list=[],mask:list=[]):
        super().__init__(6,difficulty,gameGrid,mask)
        
        self.grid.generateGrid()
        
        self.initDisplay(True)
        self.connectAllButtons(self.click)

    def click(self,i,j):
        self.changeColor(i,j) 

class Grid10x10(GridWidget):
    
    def __init__(self):
        super().__init__(10,Difficulty.BEGINNER)
            
        self.grid.mask = [[-1 for i in range(10)] for j in range(10)]
        self.grid.solution = [[-1 for i in range(10)] for j in range(10)]
        self.grid.gameGrid = [[-1 for i in range(10)] for j in range(10)]
        
        self.initDisplay()
        self.connectAllButtons(self.click)

    def click(self,i,j):
        self.changeColor(i,j)
        
class onChoixGrid(GridWidget):
    
    def __init__(self,size:int,difficulty:Difficulty=Difficulty.BEGINNER,gameGrid:list=[],mask:list=[]):
        super().__init__(size,difficulty,gameGrid,mask)
        
        self.grid.generateGrid(False)
        
        self.initDisplay(True)
        self.connectAllButtons(self.click)

    def click(self,i,j):
        self.changeColor(i,j)
        
    p = [Position(0,1),Position(0,2),Position(0,3)]
    print(list(map(lambda pos: pos.toTuple(),p)))
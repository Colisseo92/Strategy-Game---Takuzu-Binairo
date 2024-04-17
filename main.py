import sys
from datetime import timedelta
from PyQt5.QtWidgets import QApplication,QStackedLayout,QMessageBox,QDialog,QVBoxLayout,QHBoxLayout, QPushButton,QMainWindow,QWidget,QAction,QToolBar,QGridLayout,QStackedLayout,QLabel, QBoxLayout,QSlider
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QKeySequence

from customWidget import WidgetBar,GameButton
from utils import ButtonState, Difficulty, GameButtonType, getCssFile,IndicatorType,GameModeType,ErrorType,LineType
from GridWindow import Grid4x4, Grid6x6, onChoixGrid, Grid10x10
from HintWindow import HintWindowType,HintWidgetWindow,HintType
from solver import Solver,Entry
from config import WIDTH,HEIGHT
from pattern import Pattern,Patterns,PatternType
from grid_utils import Position,GridError

#REVOIR TOUT LES CODES AVEC COPY DE 2D LISTE CAR FONCTIONNE PAS
    
        
class SelectGridSizeWidget(QDialog):
    """Class that generate the window when the player wants to
    select manually a grid sizess
    """
    value_changed =  pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        
        self.mainLayout = QVBoxLayout()
        self.selected = False
        
        self.setWindowTitle("Binairo - Choose a grid size")
        self.setGeometry(300,300,500,100)
        self.setFixedWidth(500)
        
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.layout)
        self.mainLayout.addWidget(self.mainWidget)
        
        self.l = QLabel("4")
        self.l.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.l)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(4)
        self.slider.setMaximum(14)
        self.slider.setValue(4)
        self.slider.setSingleStep(2)
        self.slider.setTickInterval(2)
        self.slider.valueChanged.connect(self.changeValue)
        self.slider.sliderMoved.connect(self.correct_pos)    
        self.layout.addWidget(self.slider)
        
        self.valid = QPushButton("OK")
        self.valid.setFixedHeight(50)
        self.valid.setFixedWidth(300)
        self.layout.addWidget(self.valid)
        self.valid.clicked.connect(self.onValid)
        
        self.b = QPushButton("QUIT")
        self.b.setFixedHeight(50)
        self.b.setFixedWidth(300)
        self.layout.addWidget(self.b)
        self.b.clicked.connect(self.quit)
        
        self.setLayout(self.mainLayout)
        
    def onValid(self):
        value = self.slider.value()
        self.value_changed.emit(value)
        self.close()   
    
    def quit(self):
        self.close()
        
    def changeValue(self):
        value = self.slider.value()
        self.l.setText(str(value))
        
    def correct_pos(self,pos):
        if pos%2 != 0:
            self.slider.setValue(pos+1)
            self.l.setText(str(pos+1))
        
class MainWindow(QMainWindow):
    """Main class that is used to monitor the main window

    Args:
        QMainWindow (QMainWindow)
    """
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlag(Qt.WindowMaximizeButtonHint,False) #Prevent user to resize window
        self.setGeometry(100,100,WIDTH,WIDTH/2)
        self.setFixedWidth(WIDTH)
        self.setWindowTitle("Binairo")
        
        self.isFinished = False #Unused var
        self.gamemode = GameModeType.NONE
        self.current_time = 0
        
        self.difficulty = Difficulty.BEGINNER
        self.grid_type = "define"
        self.call_grid = lambda d : self.onGrid4(d)
        
        self.is_toolbar_displayed = False
        ###############################################
        #               WIDGET LAYOUT                 #
        ###############################################
        self.widget = QWidget(self)
        self.bottomWidget = QWidget()
        self.solveWidget = QWidget()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.addTime)
        ###############################################
        #                 LAYOUTS                     #
        ###############################################
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.bottomLayout = QGridLayout()
        self.solveLayout = QVBoxLayout()
        ###############################################
        #              LOCKED lAYOUT                  #
        ###############################################
        self.widget.setLayout(self.layout)
        
        self.setStyleSheet("background-color:#222f3e;")
        
        self.bottomWidget.setLayout(self.bottomLayout)
        self.bottomWidget.setStyleSheet("background-color:#222f3e;")
        
        self.solveWidget.setLayout(self.solveLayout)
        self.solveWidget.setStyleSheet("background-color:#222f3e;")
        
        self.bottomLayout.setSpacing(0)
        self.bottomLayout.setContentsMargins(0,0,0,0)  
        
        self.solveLayout.setSpacing(0)
        self.solveLayout.setContentsMargins(0,0,0,0)   
        self.solveLayout.setAlignment(Qt.AlignTop|Qt.AlignCenter)   
        ###############################################
        #                  WIDGETS                    #
        ###############################################
        self.grid = Grid6x6()
        
        self.solver = Solver(self.grid.grid)
        solvable_grid = self.solver.getSolvableGrid()
        self.grid.grid.setSolutionGrid(solvable_grid)
        self.grid.grid.getBeginningGridFromSolution()
        self.grid.setFixedHeight(int(WIDTH/2))
        self.grid.setFixedWidth(int(WIDTH/2))
        self.solver.setGrid(self.grid.grid)
        self.grid.resetGrid()
        ###############################################
        #              ADD TO lAYOUT                  #
        ###############################################
        #self.initActionBar()
        if self.gamemode == GameModeType.GAME:
            self.displayNormalGameMode()
        elif self.gamemode == GameModeType.SOLVING:
            self.displaySolvingGameMode()
        elif self.gamemode == GameModeType.NONE:
            self.displayMainMenu()
        
        self.setCentralWidget(self.widget)   
        
    
    def initActionBar(self) -> None:
        if self.is_toolbar_displayed == False:
            self.is_toolbar_displayed = True
            self.toolbar = QToolBar("Toolbar") #Toolbar initialisation
            self.addToolBar(self.toolbar) #Toolbar 
            """Function used to initialise the action bar and menu bar"""
            ###############################################
            #                 ACTIONS                     #
            ###############################################
            self.grid4x4 = QAction(QIcon("images/application-tile.png"),"4x4 Grid",self)
            self.grid4x4.setShortcut(QKeySequence("Ctrl+G"))
            self.grid4x4.triggered.connect(lambda x : self.onGrid4(Difficulty.BEGINNER))
            self.grid6x6 = QAction(QIcon("images/block--plus.png"),"6x6 Grid",self)
            self.grid6x6.setShortcut(QKeySequence("Ctrl+X"))
            self.grid6x6.triggered.connect(lambda x : self.OnGrid6(Difficulty.BEGINNER))
            self.choose_size = QAction(QIcon("images/block--pencil.png"),"Choose a grid size",self)
            self.choose_size.setShortcut(QKeySequence("Ctrl+C"))
            self.choose_size.triggered.connect(self.onChoice)
            
            self.beginner_level = QAction(QIcon("images/android.png"),"Beginner level",self)
            self.beginner_level.setShortcut(QKeySequence("Ctrl+D"))
            self.beginner_level.triggered.connect(self.onBeginnerLevel)
            self.medium_level = QAction(QIcon("images/android_rouge.png"),"Medium level", self)
            self.medium_level.setShortcut(QKeySequence("Ctrl+I"))
            self.medium_level.triggered.connect(self.onMediumLevel)
            
            self.grid_solv = QAction(QIcon("images/keyboard-smiley.png"),"Solve",self)
            self.grid_solv.setShortcut(QKeySequence("Ctrl+S"))
            
            self.playGameMode = QAction("Play",self)
            self.playGameMode.triggered.connect(self.displayNormalGameMode)
            self.solveGameMode = QAction("Solve", self)
            self.solveGameMode.triggered.connect(self.displaySolvingGameMode)
            
            self.game_rules = QAction(QIcon("images/balloon-smiley.png"),"Game rules",self)
            self.game_rules.setShortcut(QKeySequence("Ctrl+R"))
            self.game_rules.triggered.connect(self.onGameRule)
            
            self.author = QAction(QIcon("images/animal-monkey.png"),"Author",self)
            self.author.triggered.connect(self.onTeam)
            self.author.setShortcut(QKeySequence("Ctrl+E"))
            
            self.quit_action = QAction("Quit", self)
            self.quit_action.setShortcut(QKeySequence("Ctrl+Q"))
            self.quit_action.triggered.connect(self.onQuit)
            
            self.quit_icon_action = QAction(QIcon("images/bomb.png"),"Quit",self)
            self.quit_icon_action.triggered.connect(self.onQuit)
            ###############################################
            #                    MENU                     #
            ###############################################
            self.grid_menu = self.menuBar().addMenu("Grid")
            self.play_menu = self.menuBar().addMenu("Play")
            self.game_mode_menu = self.menuBar().addMenu("GameMode")
            self.more_menu = self.menuBar().addMenu("More")
            
            self.menuBar().addAction(self.quit_action)
            
            self.grid_menu.addAction(self.grid4x4)
            self.grid_menu.addAction(self.grid6x6)
            self.grid_menu.addAction(self.choose_size)
            
            self.play_menu.addAction(self.beginner_level)
            self.play_menu.addAction(self.medium_level)
            
            self.game_mode_menu.addAction(self.playGameMode)
            self.game_mode_menu.addAction(self.solveGameMode)
            
            self.more_menu.addAction(self.game_rules)
            self.more_menu.addSeparator()
            self.more_menu.addAction(self.author)
            ###############################################
            #              ACTION BAR                     #
            ###############################################
            self.toolbar.addAction(self.grid4x4)
            self.toolbar.addAction(self.grid6x6)
            self.toolbar.addAction(self.choose_size)
            self.toolbar.addAction(self.beginner_level)
            self.toolbar.addAction(self.medium_level)
            self.toolbar.addAction(self.game_rules)
     
    def displayMainMenu(self) -> None:
        self.main_menu_widget = QWidget(self)
        self.main_menu_layout = QVBoxLayout(self)
        self.main_menu_widget.setLayout(self.main_menu_layout)
        self.main_menu_layout.setAlignment(Qt.AlignTop|Qt.AlignCenter)
        
        self.main_menu_layout.setContentsMargins(50,50,50,50) 
        self.main_menu_layout.setSpacing(50)
        
        self.title = QLabel("BINAIRO")
        self.title.setStyleSheet("font-size:100px;font-weight:bold;letter-spacing:10px;margin-top:20px;color:white;")
        self.title.setAlignment(Qt.AlignCenter)
        
        self.play_button = GameButton(GameButtonType.CYAN,ButtonState.EMPTY)
        self.play_button.setToolTip("")
        self.play_button.setText("PLAY")
        self.play_button.connect(self.start_game)
        
        self.difficulty_button = GameButton(GameButtonType.UNFILLED,ButtonState.EMPTY)
        self.difficulty_button.setToolTip("")
        self.difficulty_button.setText("Beginner")
        self.difficulty_button.connect(self.change_difficulty)
        
        self.size_button = GameButton(GameButtonType.UNFILLED,ButtonState.EMPTY)
        self.size_button.setToolTip("")
        self.size_button.setText("4x4")
        self.size_button.connect(self.change_size)
        
        self.main_menu_layout.addWidget(self.title)
        self.main_menu_layout.addWidget(self.play_button)
        self.main_menu_layout.addWidget(self.difficulty_button)
        self.main_menu_layout.addWidget(self.size_button)
        
        self.layout.addWidget(self.main_menu_widget)
     
    def displayNormalGameMode(self) -> None:
        self.clearMainWindow()
        if not self.timer.isActive():
            self.timer.start(1000)
        ###############################################
        #                  WIDGETS                    #
        ###############################################
        self.timer_label = QLabel("{:0>8}".format(str(timedelta(seconds=self.current_time))))
        self.timer_label.setStyleSheet(getCssFile("css/resetWidgetCss.css"))
        self.timer_label.setStyleSheet("font-size:40px;font-weight:bold;letter-spacing:10px;margin:10px 0px 0px 0px;color:white;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        
        self.grid_layout = QVBoxLayout() #Stacked layout
        self.grid_layout.addWidget(self.timer_label)
        self.grid_layout.addWidget(self.grid)
        
        self.help = HintWidgetWindow(HintWindowType.CORRECT)
        self.help.display(HintType.INITIALIZE)
        self.help.setFixedWidth(int(WIDTH/2))
        self.help.setFixedHeight(int(WIDTH/2))
        
        self.health_bar = WidgetBar(self.grid.grid.maxHealth,self.grid.grid.currentHealth,IndicatorType.HEALTH)
        self.health_bar.setFixedWidth(int(WIDTH/2))

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet(getCssFile("css/windows_button.css"))
        self.verify_btn.clicked.connect(self.checkGrid)
        
        ###############################################
        #              ADD TO lAYOUT                  #
        ###############################################
        self.bottomLayout.addLayout(self.grid_layout,1,0)
        self.bottomLayout.addWidget(self.help,1,1,3,1)
        self.bottomLayout.addWidget(self.health_bar,2,0)
        self.bottomLayout.addWidget(self.verify_btn,3,0)
        #
        self.layout.addWidget(self.bottomWidget)
    
    def displaySolvingGameMode(self) -> None:
        self.clearMainWindow()
        self.clearSolveWindow()
        self.solver.solve()
        self.solver.backTrack()
        self.solver.computeMaxStep()
        if self.timer.isActive():
            self.timer.stop()
        ###############################################
        #                  WIDGETS                    #
        ###############################################
        self.timer_label = QLabel("Grid Solution")
        self.timer_label.setStyleSheet(getCssFile("css/resetWidgetCss.css"))
        self.timer_label.setStyleSheet("font-size:40px;font-weight:bold;letter-spacing:10px;margin:10px 0px 0px 120px;color:white;")
        self.timer_label.setAlignment(Qt.AlignLeft)
        
        
        self.grid_layout = QVBoxLayout() #Stacked layout
        self.grid_layout.addWidget(self.timer_label)
        self.grid_layout.addWidget(self.grid)
        
        self.text_steps = QLabel(f"Solving Mode [{self.solver.getCurrentDisplayedStep()+1}/{self.solver.getMaxStep()}]")
        self.text_steps.setStyleSheet(getCssFile("css/resetWidgetCss.css"))
        self.text_steps.setStyleSheet("font-size:30px;margin:18px 0px 25px 0px;color:white;")
        self.text_steps.setAlignment(Qt.AlignCenter)
        
        self.displayed_steps = WidgetBar(self.solver.getMaxStep(),self.solver.getCurrentDisplayedStep(),IndicatorType.STEPS)
        self.displayed_steps.setFixedWidth(WIDTH)
        
        self.solving_steps_button_widget = QWidget()
        self.solving_steps_button_widget.setStyleSheet("background-color:#222f3e;")
        self.solving_steps_button_layout = QHBoxLayout()
        
        self.previous_step_button = GameButton(GameButtonType.UNFILLED,ButtonState.EMPTY)
        self.previous_step_button.changeText("Previous")
        self.previous_step_button.connect(self.solverPreviousStep)
        self.previous_step_button.setTemporaryButtonType(GameButtonType.DISABLED)
        
        self.next_step_button = GameButton(GameButtonType.UNFILLED,ButtonState.EMPTY)
        self.next_step_button.changeText("Next")
        self.next_step_button.connect(self.solverNextStep)
        
        ###############################################
        #              ADD TO lAYOUT                  #
        ###############################################
        self.bottomLayout.addLayout(self.grid_layout,1,0,1,4)
        
        self.solving_steps_button_layout.addWidget(self.previous_step_button)
        self.solving_steps_button_layout.addWidget(self.next_step_button)
        
        self.solving_steps_button_widget.setLayout(self.solving_steps_button_layout)
        
        self.solveLayout.addWidget(self.text_steps)
        self.solveLayout.addWidget(self.displayed_steps)
        self.solveLayout.addWidget(self.solving_steps_button_widget)
        
        self.layout.addWidget(self.bottomWidget)
        self.layout.addWidget(self.solveWidget)
    
    def clearGrid(self):
        """Function that clear the layout responsible for the grid"""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
    def clearMainWindow(self):
        """Function that clear the layout used as the main window"""
        if self.timer.isActive():
            self.timer.stop()
        self.solveWidget.setParent(None)
        while self.bottomLayout.count():
            child = self.bottomLayout.takeAt(0)
            if child != None:
                if child.widget():
                    child.widget().deleteLater() 
     
    def clearSolveWindow(self):
        """Function used to clear the layout responsible for the solve window
        """
        if self.timer.isActive():
            self.timer.stop()
        while self.solveLayout.count():
            child = self.solveLayout.takeAt(0)
            if child != None:
                if child.widget():
                    child.widget().deleteLater()
    
    def solverNextStep(self):
        """Function use to display the next step in the solver mode"""
        if self.solver.getCurrentDisplayedStep()+1 == 0:
            self.previous_step_button.goBackToNormalButtonType()
        if self.solver.getCurrentDisplayedStep()+1 != self.solver.getMaxStep():
            self.solver.nextDisplayedStep()
            self.text_steps.setText(f"Solving Mode [{self.solver.getCurrentDisplayedStep()+1}/{self.solver.getMaxStep()}]")
            self.displayed_steps.update(self.solver.getCurrentDisplayedStep()+1)
            for entry in self.solver.step_dict[self.solver.getCurrentDisplayedStep()]:
                self.grid.buttons[entry.y][entry.x].setText(entry.getDisplayableValue())
                self.grid.grid.styleMask[entry.y][entry.x] = 1
            if self.solver.getCurrentDisplayedStep() - 1 >= 0:
                for entry2 in self.solver.step_dict[self.solver.getCurrentDisplayedStep()-1]:
                    self.grid.grid.styleMask[entry2.y][entry2.x] = -1
                    self.grid.buttons[entry2.y][entry2.x].buttonType = GameButtonType.UNFILLED
                    self.grid.buttons[entry2.y][entry2.x].updateStyleSheet()
            self.grid.applyStyleMask()
        if(self.solver.getCurrentDisplayedStep()+1 == self.solver.getMaxStep()):
            self.next_step_button.setTemporaryButtonType(GameButtonType.DISABLED)
               
    def solverPreviousStep(self):
        """Function used to display the previous step in the solver mode"""
        if self.solver.getCurrentDisplayedStep()+1 == self.solver.getMaxStep():
            self.next_step_button.goBackToNormalButtonType()
        if self.solver.getCurrentDisplayedStep() + 1 > 0:
            self.solver.previousDisplayedStep()
            self.text_steps.setText(f"Solving Mode [{self.solver.getCurrentDisplayedStep()+1}/{self.solver.getMaxStep()}]")
            self.displayed_steps.update(self.solver.getCurrentDisplayedStep()+1)
            if self.solver.getCurrentDisplayedStep() < self.solver.getMaxStep():
                for entry in self.solver.step_dict[self.solver.getCurrentDisplayedStep() + 1]:
                    self.grid.buttons[entry.y][entry.x].buttonType = GameButtonType.UNFILLED
                    self.grid.buttons[entry.y][entry.x].updateStyleSheet()
                    self.grid.buttons[entry.y][entry.x].setText("")
                    self.grid.grid.styleMask[entry.y][entry.x] = -1
            if self.solver.getCurrentDisplayedStep() >= 0:
                for entry2 in self.solver.step_dict[self.solver.getCurrentDisplayedStep()]:
                    self.grid.buttons[entry2.y][entry2.x].setText(entry2.getDisplayableValue())
                    self.grid.grid.styleMask[entry2.y][entry2.x] = 1
            self.grid.applyStyleMask()
        if self.solver.getCurrentDisplayedStep()+1 == 0:
            self.previous_step_button.setTemporaryButtonType(GameButtonType.DISABLED)
    
    def addTimer(self):
        self.timer_label = QLabel("{:0>8}".format(str(timedelta(seconds=self.current_time))))
        self.timer_label.setStyleSheet(getCssFile("css/resetWidgetCss.css"))
        self.timer_label.setStyleSheet("font-size:40px;font-weight:bold;letter-spacing:10px;margin:10px 0px 0px 0px;color:white;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.timer_label)
        
    def onQuit(self):
        sys.exit()
       
    def onTeam(self):
        msg = QMessageBox()
        msg.setWindowTitle("Who ?")
        msg.setIcon(QMessageBox.Icon.Information)
        
        msg.setText("Project made by Andornetti Flavio (23170128)")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        val = msg.exec_()
  
    def onGameRule(self) -> None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.NoIcon)
        msg.setWindowTitle("Binairo | Rules")
        msg.setStyleSheet("background-color:#222f3e;color:white;")
        
        msg.setText("- You must fill all the grid with only ones and zeros\n"
                    + "- Each row and column should have the same number of ones and zeros\n"
                    + "- Each row and column should have no more than two of either number adjacent to each other:"
                    + "\n\t- 001 and 110 are valid"
                    + "\n\t- 000 and 111 are not valid\n"
                    + "- Each row and column should be unique")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        val = msg.exec_()
    
    def onGrid4(self,difficulty=Difficulty.BEGINNER):
        self.clearGrid()
        self.grid = Grid4x4(difficulty)
        self.solver.setGrid(self.grid.grid)
        solvable_grid = self.solver.getSolvableGrid()
        self.grid.grid.setSolutionGrid(solvable_grid)
        self.grid.grid.getBeginningGridFromSolution()
        self.grid.setFixedHeight(int(WIDTH/2))
        self.grid.setFixedWidth(int(WIDTH/2))
        self.addTimer()
        self.grid_layout.addWidget(self.grid)
        self.solver.setGrid(self.grid.grid)
        self.grid.resetGrid()
        self.current_time = 0
        self.call_grid = lambda d : self.onGrid4(d)
        self.grid_type = "define"
        if not self.timer.isActive():
            self.timer.start(1000)
        self.setWindowTitle(f"Binairo - {self.grid.size}x{self.grid.size} | {self.grid.grid.difficulty}")
        
    def OnGrid6(self,difficulty=Difficulty.BEGINNER):
        self.clearGrid()
        self.grid = Grid6x6(difficulty)
        self.solver.setGrid(self.grid.grid)
        solvable_grid = self.solver.getSolvableGrid()
        self.grid.grid.setSolutionGrid(solvable_grid)
        self.grid.grid.getBeginningGridFromSolution()
        self.grid.setFixedHeight(int(WIDTH/2))
        self.grid.setFixedWidth(int(WIDTH/2))
        self.addTimer()
        self.grid_layout.addWidget(self.grid)
        self.solver.setGrid(self.grid.grid)
        self.grid.resetGrid()
        self.current_time = 0
        if not self.timer.isActive():
            self.timer.start(1000)
        self.grid_type = "define"
        self.call_grid = lambda d : self.OnGrid6(d)
        self.setWindowTitle(f"Binairo - {self.grid.size}x{self.grid.size} | {self.grid.grid.difficulty}")
        
    def onChoice(self):
        self.size_choice = [0,1,2]
        self.selectSize = SelectGridSizeWidget()
        self.selectSize.value_changed.connect(self.changeWindowSize)
        self.selectSize.show()
           
    def changeWindowSize(self, value):
        self.clearGrid()
        self.grid = onChoixGrid(int(value))
        self.solver.setGrid(self.grid.grid)
        solvable_grid = self.solver.getSolvableGrid()
        self.grid.grid.setSolutionGrid(solvable_grid)
        self.grid.grid.getBeginningGridFromSolution()
        self.grid.setFixedHeight(int(WIDTH/2))
        self.grid.setFixedWidth(int(WIDTH/2))
        self.addTimer()
        self.grid_layout.addWidget(self.grid)
        self.solver.setGrid(self.grid.grid)
        self.grid.resetGrid()
        self.current_time = 0
        if not self.timer.isActive():
            self.timer.start(1000)
        self.grid_type = "choice"
        self.call_grid = lambda d : self.changeWindowSize(value)
        self.setWindowTitle(f"Binairo - {self.grid.size}x{self.grid.size} | {self.grid.grid.difficulty}")
            
    def addTime(self):
        self.current_time += 1
        self.timer_label.setText("{:0>8}".format(str(timedelta(seconds=self.current_time))))     
    
    def onBeginnerLevel(self): 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Binairo - Warning")
        
        msg.setText("By changing the difficulty, you will reset the current game. Are you sure you want to continue ?")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.buttonClicked.connect(self.BeginnerDialog)

        val = msg.exec_()
        
    def BeginnerDialog(self,i):
        if i.text() == "OK":
            self.grid.changeDifficulty(Difficulty.BEGINNER)
            self.difficulty = Difficulty.BEGINNER
            self.solver.setGrid(self.grid.grid)
            self.health_bar.clear()
            self.health_bar.setMaximumValue(self.grid.grid.currentHealth)
            self.health_bar.setCurrentValue(self.grid.grid.currentHealth)
            self.health_bar.initialize()
            self.current_time = 0
            self.setWindowTitle(f"Binairo - {self.grid.size}x{self.grid.size} | {self.grid.grid.difficulty}")
        elif i.text() == "Cancel":
            pass
        
    def onMediumLevel(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Binairo - Warning")
        
        msg.setText("By changing the difficulty, you will reset the current game. Are you sure you want to continue ?")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.buttonClicked.connect(self.MediumDialog)

        val = msg.exec_()
        
    def MediumDialog(self,i):
        if i.text() == "OK":
            self.grid.changeDifficulty(Difficulty.INTERMEDIATE)
            self.difficulty = Difficulty.INTERMEDIATE
            self.solver.setGrid(self.grid.grid)
            self.health_bar.clear()
            self.health_bar.setMaximumValue(self.grid.grid.currentHealth)
            self.health_bar.setCurrentValue(self.grid.grid.currentHealth)
            self.health_bar.initialize()
            self.current_time = 0
            self.setWindowTitle(f"Binairo - {self.grid.size}x{self.grid.size} | {self.grid.grid.difficulty}")
        elif i.text() == "Cancel":
            pass

    def start_game(self) -> None:
        """Code added at the end so not optimized
        
        Code that is execute when the player click on the PLAY button
        on the main menu
        """
        self.main_menu_widget.setParent(None)
        self.gamemode = GameModeType.GAME
        self.setStyleSheet("background-color:white;")
        self.initActionBar()
        self.displayNormalGameMode()
        if(self.size_button.text() == "4x4"):
            if(self.difficulty_button.text() == "Beginner"):
                self.onGrid4(Difficulty.BEGINNER)
            elif(self.difficulty_button.text() == "Intermediate"):
                self.onGrid4(Difficulty.INTERMEDIATE)
        elif(self.size_button.text() == "6x6"):
            if(self.difficulty_button.text() == "Beginner"):
                self.OnGrid6(Difficulty.BEGINNER)
            elif(self.difficulty_button.text() == "Intermediate"):
                self.OnGrid6(Difficulty.INTERMEDIATE)
        
    def change_difficulty(self) -> None:
        if self.difficulty_button.text() == "Beginner":
            self.difficulty_button.setText("Intermediate")
            self.difficulty = Difficulty.INTERMEDIATE
        elif self.difficulty_button.text() == "Intermediate":
            self.difficulty_button.setText("Beginner")
            self.difficulty = Difficulty.BEGINNER
            
    def change_size(self) -> None:
        if self.size_button.text() == "4x4":
            self.size_button.setText("6x6")
            self.call_grid = lambda d : self.OnGrid6(d)
        elif self.size_button.text() == "6x6":
            self.size_button.setText("4x4")
            self.call_grid = lambda d : self.onGrid4(d)

    def checkGrid(self) -> None:
        position_error = self.grid.checkGrid()
        self.grid.colorGrid()
        
        if len(position_error) != 0:
            value = self.health_bar.current_value
            self.health_bar.update(value-1)
            self.health_bar.setCurrentValue(value-1)
            self.help.display(position_error[-1].getHintType())
            if self.health_bar.current_value == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.NoIcon)
                msg.setWindowTitle("You lost")
                
                msg.setText("You've used all your lives without solving the grid")
                msg.setStandardButtons(QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Abort)
                msg.buttonClicked.connect(self.end_game)
                
                val = msg.exec_()
                
                
        
        s = Solver(self.grid.grid)
        if s.isSolvable():
            self.timer.stop()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.NoIcon)
            msg.setWindowTitle("You've win")
            
            msg.setText("You just ended the grid in {:0>8}".format(str(timedelta(seconds=self.current_time))))
            msg.setStandardButtons(QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Abort)
            msg.buttonClicked.connect(self.end_game)

            val = msg.exec_()
        else:
            pass
            
    def end_game(self,i):
        if(i.text() == "Abort"):
            self.onQuit()
        elif(i.text() == "Retry"):
            if self.grid_type == "define":
                self.help.display(HintType.INITIALIZE)
                self.health_bar.setCurrentValue(self.health_bar.maximum_value)
                self.health_bar.update(self.health_bar.current_value)
                self.call_grid(self.difficulty)
            elif self.grid_type == "choice":
                self.call_grid(1)
        
app = QCoreApplication.instance()
if app is None:
    app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
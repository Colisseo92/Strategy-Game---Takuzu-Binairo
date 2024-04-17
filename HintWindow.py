from PyQt5.QtWidgets import QVBoxLayout,QWidget,QLabel,QHBoxLayout,QStackedLayout,QGridLayout
from utils import getCssFile,GameButtonType,ButtonState
from PyQt5.QtCore import Qt
from customWidget import GameButton
import enum

labelResetStyle = """
                    color: white;
                    padding: 0px 0px;
                    margin-bottom: 20px;
                    margin-top: 20px;
                    background-color: none;
                    border: none;
                    font-size: 20px;
                """

class HintWindowType(enum.Enum):
    """Enum class use to style the hint window depending on the displayed hint
    """
    
    CORRECT = ("#1dd1a1","rgba(29, 209, 161,0.3)")
    VALID = ("#feca57","rgba(254, 202, 87,0.3)")
    INCORRECT = ("#ee5253","rgba(238, 82, 83,0.3)")
    NORMAL = ("#8395a7","rgba(131, 149, 167,0.5)")
    
    def getBorderColor(self) -> str:
        """Return the color of the border of the widget that display the hint"""
        return self.value[0]
    
    def getBackgroundColor(self) -> str:
        """Return the color of the background of the widget that display the hint"""
        return self.value[1]
    
    def getStyleSheet(self) -> str:
        """Return the applicable style for the widget that display the hint"""
        style = getCssFile("css/HintWidget.css")
        style = style.replace("%background-color%",self.getBackgroundColor())
        style = style.replace("%border-color%",self.getBorderColor())
        return style
    
class HintType(enum.Enum):
    """Enum to specify different type of hint that can be given
    """
    
    ZERO_BETWEEN_ONES = [0,[1,0,1],HintWindowType.VALID]
    ONE_BETWEEN_ZEROS = [1,[0,1,0],HintWindowType.VALID]
    MORE_THAN_TWO_ZEROS = [2,{"":"","a":"0","b":"1"},HintWindowType.INCORRECT] #a's should be replaced by zeros and b by ones
    MORE_THAN_TWO_ONES = [3,{"":"","a":"1","b":"0"},HintWindowType.INCORRECT]
    COMPARING = [4,{},HintWindowType.VALID]
    VALID_MOVE = [5,"Valid move but incorrect",HintWindowType.VALID]
    CORRECT_MOVE = [6, "Valid move !",HintWindowType.CORRECT]
    INITIALIZE = [7,"",HintWindowType.NORMAL]
    TOO_MUCH_ZEROS = [8,[0,0,0],HintWindowType.INCORRECT]
    TOO_MUCH_ONES = [9,[1,1,1],HintWindowType.INCORRECT]
    
    def getPattern(self) -> list:
        """Return a valid pattern in the game as hint"""
        return self.value[1]

    def getLetterChanges(self) -> dict:
        """Return a dictionnary that is used to replace letters in a text
        by corresponding number depending off the situation"""
        return self.value[1]
    
    def getHintWindowType(self) -> HintWindowType:
        """Function that return the HintWindoType associated to the hint type"""
        return self.value[2]
    
class SimpleHintExplanationWidget(QWidget):
    """Type of hint that display a simple situation
    (only 3 grid cells in an horizontal line)
    """
    
    def __init__(self,hintType: HintType) -> None:
        super().__init__()

        number_order = hintType.getPattern()

        self.setStyleSheet(hintType.getHintWindowType().getStyleSheet())
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20,20,20,20)
        self.layout.setSpacing(20)
        
        self.SimpleHintWidget = QWidget()
        self.SimpleHintWidgetLayout = QHBoxLayout()
        self.SimpleHintWidget.setLayout(self.SimpleHintWidgetLayout)
        
        for i in range(3):
            button = GameButton(GameButtonType.UNFILLED,ButtonState.DEACTIVATED)
            button.setToolTip("")
            button.setFixedSize(100,100)
            button.setText(str(number_order[i]))
            self.SimpleHintWidgetLayout.addWidget(button)
            
        self.layout.addWidget(self.SimpleHintWidget)
        self.setLayout(self.layout)

class GridHintWidget(QWidget):
    """Type of hint that need a 3x3 grid explanation

    """
    
    def __init__(self,grid: list, letter_change: dict) -> None:
        super().__init__()
        
        self.grid = grid
        
        self.layout = QGridLayout()
        self.layout.setContentsMargins(20,20,20,20)
        self.layout.setSpacing(20)
        
        for i,line in enumerate(self.grid):
            for j,element in enumerate(line):
                button = GameButton(GameButtonType.HINT_BUTTON,ButtonState.DEACTIVATED)
                button.setToolTip("")
                button.setFixedSize(50,50)
                button.setText(letter_change[element])
                self.layout.addWidget(button,i,j)
        
        self.setLayout(self.layout)

class GridHintExplanationWidget(QWidget):
    
    def __init__(self,hintType: HintType) -> None:
        super().__init__()
        
        self.setStyleSheet(hintType.getHintWindowType().getStyleSheet())
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20,20,20,20)
        self.layout.setSpacing(20)
        
        self.mainWidget = QWidget()
        self.mainLayout = QGridLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        grid_pattern = [
                        [["","a",""],["","a",""],["","b",""]],
                        [["","b",""],["","a",""],["","a",""]],
                        [["","",""],["a","a","b"],["","",""]],
                        [["","",""],["b","a","a"],["","",""]]
                        ]
        
        self.title = QLabel("Accepted Patterns")
        self.title.setStyleSheet("""
                                color: white;
                                padding: 0px 0px;
                                margin-bottom: 0px;
                                margin-top: 0px;
                                background-color: none;
                                border: none;
                                font-size: 20px;
                                """)
        self.title.setAlignment(Qt.AlignCenter)
        
        grid_widget_1 = GridHintWidget(grid_pattern[0],hintType.getLetterChanges())
        grid_widget_2 = GridHintWidget(grid_pattern[1],hintType.getLetterChanges())
        grid_widget_3 = GridHintWidget(grid_pattern[2],hintType.getLetterChanges())
        grid_widget_4 = GridHintWidget(grid_pattern[3],hintType.getLetterChanges())
        
        self.mainLayout.addWidget(self.title,0,0,1,0)
        self.mainLayout.addWidget(grid_widget_1,1,0)
        self.mainLayout.addWidget(grid_widget_2,1,1)
        self.mainLayout.addWidget(grid_widget_3,2,0)
        self.mainLayout.addWidget(grid_widget_4,2,1)
        
        self.layout.addWidget(self.mainWidget)
        self.setLayout(self.layout)

class CompareHintExplanationWidget(QWidget):
    
    def __init__(self) -> None:
        super().__init__()
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20,20,20,20)
        self.layout.setSpacing(20)
        self.layout.setAlignment(Qt.AlignTop|Qt.AlignCenter)
        
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.firstLine = QHBoxLayout()
        self.secondLine = QHBoxLayout()
        self.solutionLine = QHBoxLayout()
        
        self.topLabel = QLabel("If in the game board we\n have the two following \n lines:")
        self.topLabel.setStyleSheet(labelResetStyle)
        self.topLabel.setAlignment(Qt.AlignCenter)
        
        self.middleLabel = QLabel("Because we can't have \n 2 similar line, \n a 0 and a 1 should be added to\n complete the second one.")
        self.middleLabel.setStyleSheet(labelResetStyle)
        self.middleLabel.setAlignment(Qt.AlignCenter)
        
        self.bottomMarginLabel = QLabel("The same rule applies for \n the columns")
        self.bottomMarginLabel.setStyleSheet(labelResetStyle)
        self.bottomMarginLabel.setAlignment(Qt.AlignCenter)
        
        for i in [1,1,0,1,0,0,1,0]:
            button = GameButton(GameButtonType.HINT_BUTTON,ButtonState.DEACTIVATED)
            button.setToolTip("")
            button.setFixedSize(50,50)
            button.setText(str(i))
            self.firstLine.addWidget(button)
            
        for i in [1,-1,0,1,0,-1,1,0]:
            button = GameButton(GameButtonType.HINT_BUTTON,ButtonState.DEACTIVATED)
            button.setToolTip("")
            if i in [1,0]:
                button.setText(str(i))
            else:
                button.setText("?")
                button.buttonType = GameButtonType.HINT_BUTTON_TO_GUESS
            button.updateStyleSheet()
            button.setFixedSize(50,50)
            self.secondLine.addWidget(button)
            
        for i in [1,2,0,1,0,3,1,0]:
            button = GameButton(GameButtonType.HINT_BUTTON,ButtonState.DEACTIVATED)
            button.setToolTip("")
            if i in [1,0]:
                button.setText(str(i))
            elif i == 2:
                button.setText("0")
                button.buttonType = GameButtonType.HINT_BUTTON_GUESSED
            elif i == 3:
                button.setText("1")
                button.buttonType = GameButtonType.HINT_BUTTON_GUESSED
            button.updateStyleSheet()
            button.setFixedSize(50,50)
            self.solutionLine.addWidget(button)
            
        self.mainLayout.addWidget(self.topLabel)
        self.mainLayout.addLayout(self.firstLine)
        self.mainLayout.addLayout(self.secondLine)
        self.mainLayout.addWidget(self.middleLabel)
        self.mainLayout.addLayout(self.solutionLine)
        self.mainLayout.addWidget(self.bottomMarginLabel)
        
        self.layout.addWidget(self.mainWidget)
        self.setLayout(self.layout)

class TextHintExplanationWidget(QWidget):
    """Hint window that only display text"""
    
    def __init__(self,hintType: HintType) -> None:
        super().__init__()
        
        self.setStyleSheet(hintType.getHintWindowType().getStyleSheet())
        
        self.hintType = hintType
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20,20,20,20)
        self.layout.setSpacing(20)
        
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.text = QLabel(hintType.value[1])
        self.text.setStyleSheet(labelResetStyle)
        self.text.setAlignment(Qt.AlignCenter)
        
        self.mainLayout.addWidget(self.text)
        self.layout.addWidget(self.mainWidget)
        
        self.setLayout(self.layout)

class HintWidgetWindow(QWidget):
    """Main window's right side to display explanation of the correct move to
    the player.
    """
    def __init__(self, window_type: HintWindowType) -> None:
        super().__init__()
        self.window_type = window_type
        
        self.layout = QStackedLayout()
        self.setStyleSheet(self.window_type.getStyleSheet())
        
        #Creation of all the different explanation
        w1 = SimpleHintExplanationWidget(HintType.ZERO_BETWEEN_ONES)
        w2 = SimpleHintExplanationWidget(HintType.ONE_BETWEEN_ZEROS)
        w3 = GridHintExplanationWidget(HintType.MORE_THAN_TWO_ZEROS)
        w4 = GridHintExplanationWidget(HintType.MORE_THAN_TWO_ONES)
        w5 = CompareHintExplanationWidget()
        w6 = TextHintExplanationWidget(HintType.VALID_MOVE)
        w7 = TextHintExplanationWidget(HintType.CORRECT_MOVE)
        w8 = TextHintExplanationWidget(HintType.INITIALIZE)
        w9 = SimpleHintExplanationWidget(HintType.TOO_MUCH_ZEROS)
        w10 = SimpleHintExplanationWidget(HintType.TOO_MUCH_ONES)
        
        # Add them in a certain order to display them when needed
        self.layout.addWidget(w1)
        self.layout.addWidget(w2)
        self.layout.addWidget(w3)
        self.layout.addWidget(w4)
        self.layout.addWidget(w5)
        self.layout.addWidget(w6)
        self.layout.addWidget(w7)
        self.layout.addWidget(w8)
        self.layout.addWidget(w9)
        self.layout.addWidget(w10)
        
        self.setLayout(self.layout)
        
    def display(self,hintType: HintType) -> None:
        """Function that take a hint type and display the layer it is in"""
        self.layout.setCurrentIndex(hintType.value[0]) #Value[0] is the layer the widget is displayed in   
        self.setStyleSheet(hintType.getHintWindowType().getStyleSheet())
from PyQt5.QtWidgets import QPushButton,QWidget,QHBoxLayout,QLabel,QVBoxLayout,QSlider
from utils import GameButtonType,ButtonState,IndicatorType,ColorType,GameButtonToolTipType
from PyQt5.QtCore import Qt
from config import WIDTH

class GameButton(QPushButton):
    """Class that is used to create all the button in the game

    Args:
        QPushButton (QPushButton): Class PyQT
    """
    
    def __init__(self, buttonType: GameButtonType, buttonState: ButtonState):
        super().__init__()
        self.buttonType = buttonType
        self.value = ""
        self.previousButtonType = None
        self.state = buttonState
        self.setToolTip(self.state.getToolTipText())
        self.setStyleSheet(buttonType.getStyleSheet() + self.state.getToolTipType().getStyleSheet())
           
    def updateStyleSheet(self):
        """Function use to change the style of a button
        depending on its type
        """
        self.setStyleSheet(self.buttonType.getStyleSheet() + self.state.getToolTipType().getStyleSheet())
        
    def changeStyleSheet(self,style):
        """Function use to change the style of the button
        to whatever is passed as a parameter 

        Args:
            style (str): New appearance
        """
        self.setStyleSheet(style + self.state.getToolTipType().getStyleSheet())
        
    def setTemporaryButtonType(self,buttonType: GameButtonType):
        """
        Function used when the player click on a button to change
        its state. Allow temporarly to know if the button has been selected by
        the player (It does not trully change the game)

        Args:
            buttonType (GameButtonType): button type we want to temporarly apply
        """
        if self.buttonType != buttonType:
            self.previousButtonType = self.buttonType
            self.buttonType = buttonType
        self.updateStyleSheet()
        
    def goBackToNormalButtonType(self):
        """Function that change the button to its previous type
        """
        if self.previousButtonType != None:
            self.buttonType = self.previousButtonType
            self.previousButtonType = None
        self.updateStyleSheet()
        
    def changeText(self,text: str) -> None:
        self.setText(text)
    
    def connect(self,func):
        """Function use to connect the button to a function that will
        be called when it is clicked on

        Args:
            func (fonction): Function that will be executed
        """
        self.clicked.connect(func)   
       
    def setState(self,button_state: ButtonState):
        """Function that change the state of the button

        Args:
            button_state (ButtonState): state of the button
        """
        self.state = button_state
        self.setToolTip(self.state.getToolTipText())
        self.updateStyleSheet()
        
    def getState(self) -> ButtonState:
        """Return the state of the button

        Returns:
            ButtonState: state of the button
        """
        return self.state
            
class WidgetBar(QWidget):
    """Class use to create dots bars to inform the player of
    some game parameters (health,hints)

    Args:
        QWidget (QWidget): class PyQT
    """
    
    def __init__(self,maximum_value:int, current_value: int,indicator_type: IndicatorType) -> None:
        super().__init__()
        self.maximum_value = maximum_value
        self.current_value = current_value
        self.indicator_size = indicator_type.getSize()
        self.indicator_type = indicator_type
        
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(int(WIDTH/self.maximum_value)-self.maximum_value*self.indicator_size)
        
        self.indicatorLabels = []
        self.initialize()
        
        self.setLayout(self.layout)
        
    def initialize(self) -> None:
        """Function to create the bar 
        """
        self.indicatorLabels = []
        for i in range(1,self.maximum_value+1):
            indicator = QLabel("")
            indicator.setAlignment(Qt.AlignCenter)
            indicator.setFixedHeight(self.indicator_size)
            indicator.setFixedWidth(self.indicator_size)
            if i <= self.current_value:
                indicator.setStyleSheet(self.indicator_type.getStyleSheet(ColorType.FILLED))
            else:
                indicator.setStyleSheet(self.indicator_type.getStyleSheet(ColorType.EMPTY))
            self.indicatorLabels.append(indicator)
            self.layout.addWidget(indicator)
            
    def clear(self) -> None:
        """Function that recolor all the dot making the bar
        so a new one can be displayed without anything left
        from the previous one
        """
        for indicator in self.indicatorLabels:
            indicator.setStyleSheet(self.indicator_type.getStyleSheet(ColorType.NONE))
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def setMaximumValue(self,value) -> None:
        self.maximum_value = value
        
    def setCurrentValue(self,value) -> None:
        self.current_value = value

    def update(self,new_value) -> None:
        """Function use to update the indicator when the value is change

        Args:
            new_value (Any): New value to be displayed
        """
        for i in range(1,self.maximum_value+1):
            if i <= new_value:
                self.indicatorLabels[i-1].setStyleSheet(self.indicator_type.getStyleSheet(ColorType.FILLED))
            else:
                self.indicatorLabels[i-1].setStyleSheet(self.indicator_type.getStyleSheet(ColorType.EMPTY))
                
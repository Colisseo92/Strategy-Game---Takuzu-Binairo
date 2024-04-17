import enum

NUMBER_CONVERSION = {0:1,1:0,-1:-1}
STRING_CONVERSION = {"0":0,"1":1,"":-1}

def getCssFile(path: str):
    with open(path) as file:
        css = file.readlines()
        css = ''.join(css).strip("\n")
    return css

class GameButtonToolTipType(enum.Enum):
    VALID = ["#1dd1a1",5]
    CORRECT = ["#feca57",5]
    DISABLED = ["#8395a7",5]
    SELECTED = ["#48dbfb",5]
    ERROR = ["#ff6b6b",5]
    
    def getBorderColor(self) -> str:
        return self.value[0]
    
    def getBorderSize(self) ->str:
        return str(self.value[1])
    
    def getStyleSheet(self):
        style = getCssFile("css/GameButtonToolTip.css")
        style = style.replace("%border-size%",self.getBorderSize())
        style = style.replace("%border-color%",self.getBorderColor())   
        return str(style)

class ButtonState(enum.Enum):
    EMPTY = [0,"Empty","",GameButtonToolTipType.CORRECT]
    FILLED = [1,"Filled","This button is filled",GameButtonToolTipType.VALID]
    DEACTIVATED = [2,"Deactivated","This button was part of the beginning grid",GameButtonToolTipType.DISABLED]
    SELECTED = [3,"Selected","This button is selected",GameButtonToolTipType.SELECTED]
    FILLED_VALID = [4,"Filled","This button is filled but it is to early to determine if it is at the right position",GameButtonToolTipType.CORRECT]
    
    def toString(self) -> str:
        return self.value[1]
    
    def getValue(self) -> int:
        return self.value[0]
    
    def getToolTipType(self) -> GameButtonToolTipType:
        return self.value[3]
    
    def getToolTipText(self) -> str:
        return self.value[2]
    
class ErrorName(enum.Enum):
    TOO_MANY_ONES = ["Too many ones in the line"]
    TOO_MANY_ZEROS = ["Too many zeros in the line"]
    LINE_SIMILAR = ["Two lines are the same"]
    COLUMN_SIMILAR = ["Two columns are the same"]
    THREE_ZEROS = ["Three zeros follow each other"]
    THREE_ONES = ["Three ones follow each other"]
    
    def getErrorText(self) -> str:
        return self.value[0]
    
class ErrorType(enum.Enum):
    LINE_ERROR = [0]
    COLUMN_ERROR = [1]
    PATTERN_ERROR = [2]
    
    def getInt(self) -> int:
        return self.value[0]
    
class ClueType(enum.Enum):
    ONE_BETWEEN_ZERO = "OneBetweenZero"
    ZERO_BETWEEN_ONE = "ZeroBetweenOne"
    ONLY_TWO_ZEROS = "OnlyTwoZeros"
    ONLY_TWO_ONES = "OnlyTwoOnes"
    
class ColorType(enum.Enum):
    FILLED = 0
    EMPTY = 1
    NONE = 2
    
class Difficulty(enum.Enum):
    BEGINNER = (6,6,3,40)
    INTERMEDIATE = (3,3,1,30)
    HARD = (3,0,1,20)
    
    
    def getGridGenerationHint(self):
        """Return the number of initial values given to the player
        depending off the difficulty"""
        return self.value[2]
    
    def getDifficultyHealth(self) -> int:
        """Return the health point available for the difficulty"""
        return self.value[0]
    
    def getDifficultyHints(self) -> int:
        """Return the number of hint available for the difficulty"""
        return self.value[1]
    
    def getPercentageShown(self) -> int:
        return self.value[3]
    
class EntryType(enum.Enum):
    FILLED = 0
    PLACEHOLDER = 1
    
class GameButtonType(enum.Enum):
    """Enumeration permettant la gestion de l'affichage du plateau de jeu

    ex: CORRECT = (background-color,border-color,color,hover_color)

    Args:
        enum (_type_): _description_
    """
    CORRECT = ("rgba(29, 209, 161,0.3)","#1dd1a1","#1dd1a1","rgba(29, 209, 161,0.5)","solid",0,0,30)
    VALID = ("rgba(254, 202, 87,0.3)","#feca57","#feca57","rgba(254, 202, 87,0.5)","solid",0,0,30)
    INCORRECT = ("rgba(255, 107, 107,0.3)","#ff6b6b","#ff6b6b","rgba(255, 107, 107,0.5)","solid",0,0,30)
    DISABLED = ("rgba(131, 149, 167,0.3)","#8395a7","#FFFFFF","rgba(131, 149, 167,0.3)","solid",0,0,30)
    UNFILLED = ("rgba(200, 214, 229,0.3)","#c8d6e5","#c8d6e5","rgba(200, 214, 229,0.5)","solid",0,0,30)
    SELECTED = ("rgba(72, 219, 251,0.3)","#48dbfb","#48dbfb","rgba(72, 219, 251,0.5)","double",0,0,30)
    HINT_BUTTON = ("rgba(200, 214, 229,0.3)","#c8d6e5","#c8d6e5","rgba(200, 214, 229,0.5)","solid",0,0,20)
    HINT_BUTTON_TO_GUESS = ("rgba(72, 219, 251,0.3)","#48dbfb","#48dbfb","rgba(72, 219, 251,0.5)","double",0,0,20)
    HINT_BUTTON_GUESSED = ("rgba(200, 214, 229,0.3)","#c8d6e5","#1dd1a1","rgba(200, 214, 229,0.5)","solid",0,0,20)
    SHOW_AFTER_NUMBER_POSITION = ("rgba(155, 89, 182,0.3)","#9b59b6","#9b59b6","rgba(155, 89, 182,0.3)","solid",15,25,30)
    DEACTIVATED = ("rgba(200, 214, 229,0.3)","#ff6b6b","#c8d6e5","rgba(200, 214, 229,0.3)","solid",0,0,30)
    CYAN = ("rgba(26, 188, 156,0.3)","#1abc9c","#1abc9c","rgba(26, 188, 156,0.5)","solid",0,0,30)
    DARK_CYAN = ("rgba(131, 149, 167,0.3)","#1abc9c","#1abc9c","rgba(131, 149, 167,0.3)","solid",0,0,30)
    GREEN = ("rgba(46, 204, 113,0.3)","#2ecc71","#2ecc71","rgba(46, 204, 113,0.5)","solid",0,0,30)
    DARK_GREEN = ("rgba(131, 149, 167,0.3)","#2ecc71","#2ecc71","rgba(131, 149, 167,0.3)","solid",0,0,30)
    BLUE = ("rgba(52, 152, 219,0.3)","#3498db","#3498db","rgba(52, 152, 219,0.5)","solid",0,0,30) 
    DARK_BLUE = ("rgba(131, 149, 167,0.3)","#3498db","#3498db","rgba(131, 149, 167,0.3)","solid",0,0,30)
    PURPLE = ("rgba(155, 89, 182,0.3)","#9b59b6","#9b59b6","rgba(155, 89, 182,0.5)","solid",0,0,30) 
    DARK_PURPLE = ("rgba(131, 149, 167,0.3)","#9b59b6","#9b59b6","rgba(131, 149, 167,0.3)","solid",0,0,30)
    YELLOW = ("rgba(241, 196, 15,0.3)","#f1c40f","#f1c40f","rgba(241, 196, 15,0.5)","solid",0,0,30)
    DARK_YELLOW = ("rgba(131, 149, 167,0.3)","#f1c40f","#f1c40f","rgba(131, 149, 167,0.3)","solid",0,0,30) 
    ORANGE = ("rgba(230, 126, 34,0.3)","#e67e22","#e67e22","rgba(230, 126, 34,0.5)","solid",0,0,30)
    DARK_ORANGE = ("rgba(131, 149, 167,0.3)","#e67e22","#e67e22","rgba(131, 149, 167,0.3)","solid",0,0,30) 
    RED = ("rgba(231, 76, 60,0.3)","#e74c3c","#e74c3c","rgba(231, 76, 60,0.5)","solid",0,0,30)
    DARK_RED = ("rgba(131, 149, 167,0.3)","#e74c3c","#e74c3c","rgba(131, 149, 167,0.3)","solid",0,0,30)
    
    def getDeactivatedButtonColorList() -> list:
        return [GameButtonType.DARK_BLUE,GameButtonType.DARK_PURPLE,GameButtonType.DARK_YELLOW,GameButtonType.DARK_ORANGE,GameButtonType.DARK_RED]
        
    def getActivatedButtonColorList() -> list:
        return [GameButtonType.BLUE,GameButtonType.PURPLE,GameButtonType.YELLOW,GameButtonType.ORANGE,GameButtonType.RED]
    
    def getBackgroundColor(self) -> str:
        return self.value[0]
    
    def getBorderColor(self) -> str:
        return self.value[1]
    
    def getColor(self) -> str:
        return self.value[2]
    
    def getHoverColor(self) -> str:
        return self.value[3]
    
    def getBorderType(self) -> str:
        return self.value[4]
    
    def getLeftPadding(self) -> int:
        return self.value[5]
    
    def getRightPadding(self) -> int:
        return self.value[6]
    
    def getFontSize(self) -> int:
        return self.value[7]
    
    def getStyleSheet(self):
        style = getCssFile("css/GameButton.css")
        style = style.replace("%background-color%",self.getBackgroundColor())
        style = style.replace("%color%",self.getColor())
        style = style.replace("%border-type%",self.getBorderType())
        style = style.replace("%border-color%",self.getBorderColor())
        style = style.replace("%hover-color%",self.getHoverColor())
        style = style.replace("%left-padding%",str(self.getLeftPadding()))
        style = style.replace("%right-padding%",str(self.getRightPadding()))
        style = style.replace("%font-size%",str(self.getFontSize()))
        return str(style)
     
class GameModeType(enum.Enum):
    GAME = 0
    SOLVING = 1
    NONE = 2

class IndicatorType(enum.Enum):
    """TYPE = (SIZE,FILLED_COLOR,EMPTY_COLOR)

    Args:
        enum (_type_): _description_
    """
    HEALTH = (30,"#ee5253","#c8d6e5")
    HINT = (30,"#ff9ff3","#c8d6e5")
    STEPS = (20,"#3498db","#c8d6e5")
    
    def getSize(self) -> int:
        return self.value[0]
    
    def getFilledColor(self) -> str:
        return self.value[1]
    
    def getEmptyColor(self) -> str:
        return self.value[2]
    
    def getStyleSheet(self,color_type:ColorType) -> str:
        style = getCssFile("css/GameIndicator.css")
        if color_type == ColorType.EMPTY:
            style = style.replace("%color%",self.getEmptyColor())
        elif color_type == ColorType.FILLED:
            style = style.replace("%color%",self.getFilledColor())
        elif color_type == ColorType.NONE:
            style = style.replace("%color%","#222f3e")
        style = style.replace("%radius%",str(int(self.getSize()/2)))
        return style
    
class IndiceType(enum.Enum):
    LINE_VALID = "Le coup est valide \nmais pas correct"
    LINE_CORRECT = "Le coup est correcte"
    LINE_SIMILAR = "En comparant une ligne déjà remplie avec une ligne\nà laquelle il manque 2 valeurs, si toutes\nles valeurs correspondent, alors on peut remplir la ligne\nà laquelle il manque deux valeurs."
    ONE_BETWEEN_ZERO = "Entre deux 0, il ne peut y avoir qu'un 1"
    ZERO_BETWEEN_ONE = "Entre deux 1, il ne peut y avoir qu'un 0"
          
class LineType(enum.Enum):
    COLUMN = 0
    HORIZONTAL = 1
    
def isLinesDifferent(line1,line2) -> bool:
    total = 0 #sum of each grid lines
    for t in zip(line1,line2): #creation of a tuple for each value of each line
        total += abs(t[0] - t[1]) #if they are similare, then substracting them should give 0
    return total != 0 #if all the line are the same the sum should be 0

def isAlmostSimilar(line1,line2):
    count = 0
    for i in range(len(line1)):
        if line1[i] != -1 or line2[i] != -1:
            count += 1 if line1[i] == line2[i] else 0
    return count >= 4

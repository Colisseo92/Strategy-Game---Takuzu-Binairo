class Debuger:
    
    def __init__(self,active:bool=False):
        self.active = active
        
    def setActive(self) -> None:
        """Set the debuger active so that Log message would be displaed in console"""
        self.active = True
        
    def setUnactive(self) -> None:
        """Set the debuger active so tha Log message won't show in console"""
        self.active = False
        
    def isActive(self) -> bool:
        """Function to know wether or not the debuger is active

        Returns:
            bool: True if active False if not
        """
        return self.active
    
    def Log(self,message: str, prefix: str="Debug") -> None:
        """Function to display message in console

        Args:
            message (str): Message to display
            prefix (str, optional): Prefix displayed in console. Defaults to "Debug".
        """
        if self.active:
            print(f"[{prefix}] >> {message}")
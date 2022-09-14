from turtle import color
import colorama
class Styles:
    def __init__():
        colorama.init()
    
    INFO = ''.join(colorama.Fore.CYAN,"[INFO] ",colorama.Style.RESET_ALL)
    DEBG = ''.join(colorama.Fore.BLACK,"[DEBUG] ",colorama.Style.RESET_ALL)
    ERR  = ''.join(colorama.Fore.RED,"[ERROR] ",colorama.Style.RESET_ALL)
    ALRT = ''.join(colorama.Fore.YELLOW,"[ALERT] ",colorama.Style.RESET_ALL)
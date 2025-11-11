
import tkinter as tk
from ui.gui import AppGUI
from core.log_config import logger

def main():
    logger.info("Iniciando aplicación principal (main.py)")
    root = tk.Tk()
    app = AppGUI(root)
    try:
        root.mainloop()
    except Exception as e:
        logger.exception("Error fatal en loop principal: %s", e)
    finally:
        logger.info("Aplicación finalizada.")

if __name__ == "__main__":
    main()

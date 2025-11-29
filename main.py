from logic import *

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Logic()
    ui.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
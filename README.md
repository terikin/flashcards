# Flashcards
Math Facts practice program to help kids learn addition, multiplication tables, etc.

# Setup
1. Download this repository (or use `git clone ...`).
1. Install Python for your operating system (https://www.python.org/downloads/).
1. Open a terminal and browse to the downloaded files (or local clone of the git repository).
1. Install dependencies using:

        python -m pip install -r requirements.txt

1. Run the program by calling:

        python flashcards_gui.py


# Usage
- The main program window allows specifying names for multiple profiles (e.g. for each child).  Click the "Add Config" button at the top left and then type a new name in the drop-down box.  Once a practice session is started, the settings are saved and the new name will be available in the drop-down selection in the future.
- Options:
    - "Response time for a problem to be mastered" - how quickly (in seconds) the user must correctly answer a problem before it is considered to be complete.
    - Minimum/maximum values - determine how large a problem set will be created and with what numbers.
- Mode selection buttons (Addition, Subtraction, Multiplication, Division)
    - Clicking any of these buttons will begin the practice session based on the given settings.
    - For example, if the min value is 3 and the max is 5, and "Addition" is clicked, then there will be 9 practice problems, including 3+3, 3+4, 3+5, 4+3, ..., 5+4, 5+5
- Once the practice session starts, the problems are presented in a random order.
- In order for a problem to be removed from the practice set and marked as completed:
    - The number of correct answers must be greater than the number of incorrect answers.
    - The most recent response must be faster than the response time threshold.
- Once all problems have been completed satisfying the above criteria, the window displays a list of all the problems from the practice set, sorted with the worst/slowest problems at the top.  This output can be selected, copied, and pasted elsewhere if desired.  It is also stored to a log file as described below.

# Notes
- Settings for each profile/child (the drop-down box at the top of the main application window) are stored in various locations depending on your operating system.  Places to check include:
    - Linux:  `~/.config/flashcards`
    - Windows:  `C:\Users\[your username]\AppData\Local\flashcards`
    - Mac:  `~/Library/Application Support/flashcards`
- By default, the output from each session is stored in a text log file in `~/Desktop/`  The output location for each profile can by changed by editing the above-mentioned profile/config files.

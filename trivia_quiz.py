# API Fed Trivia Quiz
# By: Riley Johnson
# 11/30/2020
import requests # importing the api
import keyboard # reading raw key input without using enter key
import curses # allowing for more advance terminal output
import time 
import random
import html # decoding html strings

screen = curses.initscr()

# Define quiz configuration options
categories = ["General", "Books", "Film", "Music", "Theatre", "Television", "Video Games", "Board Games", "Science and Nature", "Computers", "Math", "Mythology", 
"Sports", "Geography", "History", "Politics", "Arts", "Celebrities", "Animals", "Vehicles", "Comics", "Gadgets", "Manga", "Cartoons", "Random"]
difficulty = ["Easy", "Medium", "Hard"]
choices = ['True and False', 'Multiple Choice']
choicesFormat = ['boolean', 'multiple']

# Function menu creates a user interface for an array
# @param {list} are the options the user can choose
# @param {str} is the text to display at the top of the menu
# @param {bool} is if the ui should scroll or be static, better for longer lists
# @return {int} is the index of the option that the user chose from array param
def menu (array, name, scroll):
    global score
    global trials
    index = 0
    if scroll == True:
        scrollDisplay(array, index, name)
    else:
        staticDisplay(array, index, name)
    while True:
        key = keyboard.read_key()
        if key == "up":
            index = (index - 1)%len(array)
        elif key == "down":
            index = (index + 1)%len(array)
        elif key == "enter":
            return index  
        elif key == "esc":
            if trials == 0:
                sentence = 'No questions answered?'
            else:
                sentence = f'You scored {score}/{trials} or {int(score/trials*100)}%'
            screen.clear()
            screen.addstr(sentence)
            screen.refresh()
            time.sleep(5)
            exit(sentence)
        if scroll == True:
            scrollDisplay(array, index, name)
        else:
            staticDisplay(array, index, name)
        time.sleep(0.2)
# Specifically creates the output for menu function
# @param {list} are the options the user can choose
# @param {int} is the index of what to display as selected
# @param {str} is the text to display at the top of the menu
# @return None
def staticDisplay (array, index, name):
    screen.clear()
    screen.addstr(f"{name} (Using Arrows)\n")
    for l in array:
        if l == array[index]:
            screen.addstr(f"> {html.unescape(l).strip()}\n")
        else:
            screen.addstr(f"  {html.unescape(l).strip()}\n")
    screen.refresh()
# Specifically creates the output for menu function
# @param {list} are the options the user can choose
# @param {int} is the index of what to display in the scroll wheel
# @param {str} is the text to display at the top of the menu
# @return None
def scrollDisplay (array, index, name):
    screen.clear()
    screen.addstr(f"{name} (Using Arrows)\n")
    screen.addstr(f"  {array[(index - 1)%len(array)]}\n")
    screen.addstr(f"> {array[index]}\n")
    screen.addstr(f"  {array[(index + 1)%len(array)]}\n")
    screen.refresh()
# Display a message for a certain time
# @param {str, bool} is the message to display, None to display nothing
# @param {int, float} is how long to display the message
# @return None
def pause (dur, msg):
    screen.clear()
    if msg != None:
        screen.addstr(msg)
    screen.refresh()
    time.sleep(dur)

# Ask all the configuration questions
pause(2.5, "> Use Arrow keys to navigate.\n> Use Esc to exit at any time.")
cat = menu(categories, "Select your Category", True) + 9
pause(0.3, None)
diff = difficulty[menu(difficulty, "Select your Difficulty", False)]
pause(0.3, None)
qtype = choicesFormat[menu(choices, "Select your Question Type", False)]
pause(0.3, None)

# Predefine so there are no duplicate questions
pastQuestions = []
repetitions = 0
# Predefine score based variables
score = 0
trials = 0
while True:
    # Create exception for random category
    if cat == 33:
        randCat = random.randint(9, 32)
        apiReturn = requests.get(f"https://opentdb.com/api.php?amount=1&category={randCat}&difficulty={diff.lower()}&type={qtype}").json()
    else:
        apiReturn = requests.get(f"https://opentdb.com/api.php?amount=1&category={cat}&difficulty={diff.lower()}&type={qtype}").json()
    # Check if API returned successfully 
    if apiReturn["response_code"] != 0:
        exit("Issue with API.")
    question = apiReturn["results"][0]["question"]
    # Make sure its not a repeat question, if not resets number of consecutive repeat questions, and adds question to watch list
    if question not in pastQuestions:
        repetitions = 0
        pastQuestions.append(question)
        # Predefine variables so I feel happier
        correct = apiReturn["results"][0]["correct_answer"]
        options = apiReturn["results"][0]["incorrect_answers"] + [correct]
        random.shuffle(options)
        # Make exception for random category... again
        if cat == 33:
            answer = options[menu(options, f"{categories[randCat-9]}: {html.unescape(question)}", False)]
        else:
            answer = options[menu(options, html.unescape(question), False)]
        # Check answer and add question to total
        if answer.lower() == correct.lower():
            score += 1
            pause(0.75, "Correct! Score + 1.")
        else:
            pause(1.75, f"Incorrect! The correct answer was {html.unescape(correct)}.")
        trials += 1
    else:
        repetitions += 1
        # Early end procedure
        if repetitions > 10:
            screen.clear()
            screen.addstr("We seem to have run out of questions. :/\n")
            screen.addstr(f'You scored {score}/{trials} or {int(score/trials*100)}%')
            screen.refresh()
            time.sleep(5)
            exit(f'We seem to have run out of questions.\nYou scored {score}/{trials} or {int(score/trials*100)}%')
curses.endwin()
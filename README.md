# Anki Stats Generator
#### Video Demo:  ```https://youtu.be/piS_TZCJ9UI```
#### Description:


### The purpose of this tool

This Python script is able to read data from an **Anki Deck Package** (.apkg) and show some stats about it on an html page. This tool was created as the final project for CS50P 2026.


### What is an "Anki Deck Package"

Anki is a flash card program. The idea is simple: you get a question, you try to answer it, anki shows the answer and you say if you answered correctly or not. It is based on active recall testing and spaced repetition. For more details about anki: ```https://docs.ankiweb.net/background.html```.

Each question-answer group represents a card and multiple cards together form a deck. This deck can be exported as a file ending in **.apkg**. For more details: ```https://docs.ankiweb.net/importing/packaged-decks.html```


### Tutorial on how to use it

Open a terminal window and be sure that the project and the Anki Deck Package are in the working directory

Create a virtual environment:

```
python -m venv .venv
```

Activate the virtual environment:

Windows:

```
.\.venv\Scripts\activate
```
Linux / MacOS:

```
source .venv/bin/activate
```

Install requirements:
```
pip install -r requirements.txt
```

Run tool:
```
python project.py <Name_of_anki_deck_package.apkg>
```
For our example it will be:
```
python project.py .\data\input\LearnDutch.org-1000.apkg
```

After a few seconds the program will confirm that the html file with the statistics of the Anki Deck Package has been created.


### The tool under the hood

One interesting fact about an Anki Deck Package is that the .apkg file is actually a zip file in disguise. Once unzipped, in the folder we can find multiple media files but more importantly, a compressed db file that contains all data about a user activity on that deck. The db file is compressed using the **zstandard**, a file compression algorithm developed by Meta. More information about the zstandard: ```https://facebook.github.io/zstd/```

The tool does the following:

- unzips the .apkg file in a temporary directory
- decompresses the db
- extracts data from the db using SQL
- creates 5 graphs using the extracted data
- combines the graphs and adds them in an html file
- deletes the temporary directory


### What statistics does the Anki Stats Generator show?

The tool shows 5 graphs:

- Card counts
  - the number of cards in the deck and their type
  - there are multiple types of cards like new for cards never seen, young for cards that are not stable in the memory and mature for cards that are well remembered

- Button breakdown
  - the number of times each button has been pressed
  - there are 4 buttons in Anki (again, hard, good and easy) and review time is influenced based on them

- Top 10 Leeches
  - a "leech" is a card that has been forgotten a lot of times by the user
  - in other words this graph shows the most difficult cards

- Top 10 Mastered cards
  - a mastered (officially called "mature") card has a review time greater than 20 days
  - the graph shows the most known cards from the deck

- Overall retention rate:
  - shows how many times a "passed" button has been pressed in relation to a "failed" button
  - hard, good and easy are all three passed buttons and again is the only failed button


### File listing

Here is a list of all the files that can be found in the package:

- README.md
  - the documentation for the project and the file you are currently reading
- project.py
  - the file containing all the code for the tool to run
- test_project.py
  - testing functionality for the tool to ensure that everything works as expected
- requirements.txt
  - file that contains all the Python modules required for the tool to run


### Design choices

The reason I came up with this idea is quite simple. For the past month I have been learning Dutch using an Anki deck that contains the most used 1000 words of this language. I have been studying every day and I always loved to see at the end of my daily session the stats that Anki presents. This gave me the idea to create my own statistics using python.

I have changed my mind a few times during the creation of this project. For example I was planning to have all graphs in the terminal and not in a file but unfortunately that is not really possible. Maybe it could have been if I had my own module for drawing terminal graphs but that would have been beyond the scope of CS50P. Then I had to decide between what modules to use. I had either plotly which is easier but misses some customization features or matplotlib which has all the customization in the world but is definitely harder to implement. Because some graphs for an Anki deck do not require anything more than some basic drawings to get its point across, in the end I chose plotly.


### Info about the author 

- Name: Luc Theodor Ferrant
- Profession: cybersecurity student of Howest University of Applied Sciences
- Date of project creation: **2026-08-05**


    
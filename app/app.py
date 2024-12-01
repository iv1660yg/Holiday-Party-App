# Importing necessary modules from the Flask framework
from flask import Flask, render_template, request, redirect, url_for, session

# Importing the sqlite3 module to interact with SQLite databases
import sqlite3

# Importing the os module to interact with the operating system
import os

# Importing the random module to generate random numbers
import random

# Importing defaultdict from the collections module to create dictionaries with default values
from collections import defaultdict


app = Flask(__name__)

# Set the secret key for session management
app.secret_key = 'f8bda8a97b9c4c7ea0280dc6e08fdb7a'  # Replace with your own secure key

# Ensure the database is in the correct directory
def get_db_connection():
    db_path = os.path.join(os.getcwd(), 'app', 'database.db')  # Full path to the DB
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database (if it doesn't already exist)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables for votes, trivia scores, and bingo scores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        voter_name TEXT NOT NULL,
        vote_item TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trivia_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        score INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bingo_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        score INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leadership_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        questions_count INTEGER NOT NULL,
        predicted_score INTEGER NOT NULL,
        actual_score INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

# Initialize the database
init_db()


@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/vote')
def vote():
    return render_template('vote.html')

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    category = request.form['category']
    voter_name = request.form['voter_name']
    vote_item = request.form['vote_item'].strip().lower()  # Convert to lowercase
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user has already voted in the selected category
    cursor.execute("SELECT * FROM votes WHERE category = ? AND LOWER(vote_item) = ? AND LOWER(voter_name) = ?", 
                   (category, vote_item, voter_name.lower()))
    existing_vote = cursor.fetchone()

    if existing_vote:
        # User has already voted, show an error message
        return render_template('already_voted.html')

    # Otherwise, insert the vote into the database
    cursor.execute("INSERT INTO votes (category, voter_name, vote_item) VALUES (?, ?, ?)",
                   (category, voter_name, vote_item))
    conn.commit()
    conn.close()

    # Redirect to thank you page
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard/leaderboard_landing.html')  # New landing page for all leaderboards

@app.route('/leaderboard_vote')
def leaderboard_vote():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the votes for each category and count them
    cursor.execute("""
    SELECT category, vote_item, COUNT(*) as votes
    FROM votes
    GROUP BY category, vote_item
    ORDER BY category, votes DESC
    """)
    leaderboard_data = cursor.fetchall()
    conn.close()

    # Mapping categories to friendly names
    category_map = {
        'potluck_food': 'Best Potluck Food',
        'potluck_side_dish': 'Best Potluck Side Dish',
        'holiday_treats': 'Best Holiday Treats',
        'board_game': 'Best Board Game',
        'holiday_attire': 'Best Holiday Attire'
    }

    # Pass data to the template along with the category map
    return render_template('leaderboard/leaderboard_vote.html', leaderboard_data=leaderboard_data, category_map=category_map)

@app.route('/get_leading_items', methods=['GET'])
def get_leading_items():
    category = request.args.get('category', '')
    if not category:
        return {"items": []}

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the top items for the selected category
    cursor.execute("""
        SELECT vote_item, COUNT(*) as votes
        FROM votes
        WHERE category = ?
        GROUP BY vote_item
        ORDER BY votes DESC
        LIMIT 5
    """, (category,))
    results = cursor.fetchall()
    conn.close()

    # Return the data as JSON
    items = [{"name": row["vote_item"], "votes": row["votes"]} for row in results]
    return {"items": items}



# Holiday Trivia Game Routes
# General Holiday Trivia Questions and Answers
questions = {
    'general_holiday_trivia': {
        'round_1': [
            {'question': 'What is the most popular Christmas song of all time?', 'options': ['Jingle Bells', 'Silent Night', 'White Christmas', 'All I Want for Christmas Is You'], 'answer': 2},
            {'question': 'Which country is credited with starting the tradition of putting up a Christmas tree?', 'options': ['Germany', 'Norway', 'Sweden', 'Finland'], 'answer': 0},
            {'question': 'What is the name of the Grinch\'s dog in the movie "How the Grinch Stole Christmas"?', 'options': ['Max', 'Sam', 'Buddy', 'Charlie'], 'answer': 0},
            {'question': 'In the song "The Twelve Days of Christmas," what is given on the seventh day?', 'options': ['Seven swans a-swimming', 'Seven geese a-laying', 'Seven maids a-milking', 'Seven lords a-leaping'], 'answer': 0},
            {'question': 'Which reindeer is known for having a red nose?', 'options': ['Dasher', 'Dancer', 'Prancer', 'Rudolph'], 'answer': 3},
            {'question': 'What is the name of the main character in "The Nightmare Before Christmas"?', 'options': ['Jack Skellington', 'Oogie Boogie', 'Sally', 'Dr. Finkelstein'], 'answer': 0},
            {'question': 'Which holiday drink is made with milk, cream, sugar, whipped egg whites, and egg yolks?', 'options': ['Eggnog', 'Hot chocolate', 'Mulled wine', 'Apple cider'], 'answer': 0},
            {'question': 'What is the traditional flower of Christmas?', 'options': ['Poinsettia', 'Rose', 'Lily', 'Tulip'], 'answer': 0},
            {'question': 'In "A Christmas Carol," what is the first name of Scrooge?', 'options': ['Ebenezer', 'Jacob', 'Bob', 'Fred'], 'answer': 0},
            {'question': 'Which country is the largest exporter of Christmas trees?', 'options': ['Canada', 'United States', 'Denmark', 'Germany'], 'answer': 0},
            {'question': 'What is the most popular Christmas beverage in the United States?', 'options': ['Eggnog', 'Hot chocolate', 'Cider', 'Mulled wine'], 'answer': 1},
            {'question': 'Which holiday character is known for saying "Ho Ho Ho"?', 'options': ['Santa Claus', 'Frosty the Snowman', 'Rudolph', 'The Grinch'], 'answer': 0},
            {'question': 'In the movie "Love Actually," what is the name of the British prime minister played by Hugh Grant?', 'options': ['David Cameron', 'Peter Grant', 'John Major', 'Billy Mack'], 'answer': 1},
            {'question': 'Which popular holiday song was written by Irving Berlin in 1942?', 'options': ['Jingle Bell Rock', 'White Christmas', 'Silent Night', 'Feliz Navidad'], 'answer': 1},
            {'question': 'In "Batman Returns," what is the real name of the Penguin?', 'options': ['Oswald Cobblepot', 'Bruce Wayne', 'Edward Nygma', 'Harvey Dent'], 'answer': 0},
            {'question': 'In *Futurama*, what is the name of the robot who tries to become Santa Claus?', 'options': ['Bender', 'Robot Santa', 'Frybot', 'Zoidberg'], 'answer': 1}, 
        ],
        'round_2': [
            {'question': 'In "Home Alone," where are the McCallisters going on vacation when they leave Kevin behind?', 'options': ['Paris', 'London', 'New York', 'Rome'], 'answer': 0},
            {'question': 'What is the name of the guardian angel who helps George Bailey in "It\'s a Wonderful Life"?', 'options': ['Clarence', 'Michael', 'Gabriel', 'Raphael'], 'answer': 0},
            {'question': 'In "Elf," what is the first rule of The Code of Elves?', 'options': ['Treat every day like Christmas', 'There\'s room for everyone on the Nice List', 'The best way to spread Christmas cheer is singing loud for all to hear', 'Always be kind to others'], 'answer': 0},
            {'question': 'Which actor played six different roles in "The Polar Express"?', 'options': ['Tom Hanks', 'Tim Allen', 'Jim Carrey', 'Will Ferrell'], 'answer': 0},
            {'question': 'In "A Charlie Brown Christmas," who directs the Christmas play?', 'options': ['Charlie Brown', 'Lucy', 'Linus', 'Snoopy'], 'answer': 0},
            {'question': 'What is the name of the town in "The Nightmare Before Christmas"?', 'options': ['Halloween Town', 'Christmas Town', 'Spooky Town', 'Pumpkin Town'], 'answer': 0},
            {'question': 'Which holiday movie features a cameo by Donald Trump?', 'options': ['Home Alone 2: Lost in New York', 'The Santa Clause', 'Jingle All the Way', 'Miracle on 34th Street'], 'answer': 0},
            {'question': 'In "The Muppet Christmas Carol," who plays Scrooge?', 'options': ['Michael Caine', 'Kermit the Frog', 'Gonzo', 'Fozzie Bear'], 'answer': 0},
            {'question': 'In the *Seinfeld* episode "The Pick," what gift does George give to Susan for Christmas?', 'options': ['A velvet painting', 'A clock', 'A framed photo', 'A VHS tape'], 'answer': 0},
            {'question': 'What is the name of the Grinch\'s love interest in "How the Grinch Stole Christmas"?', 'options': ['Martha May Whovier', 'Cindy Lou Who', 'Betty Lou Who', 'Donna Lou Who'], 'answer': 0},
            {'question': 'What is the name of the fictional reindeer who appeared in the 1999 animated special "Olaf’s Frozen Adventure"?', 'options': ['Stormy', 'Dancer', 'Blitzen', 'Rudy'], 'answer': 3},
            {'question': 'In what year did the tradition of the White House Christmas tree start?', 'options': ['1920', '1942', '1851', '1967'], 'answer': 2},
            {'question': 'In *The Simpsons* episode "Miracle on Evergreen Terrace," what causes the Simpson family’s Christmas to go wrong?', 'options': ['Their house burns down', 'Maggie breaks the tree', 'Homer loses his job', 'Bart’s prank'], 'answer': 0},
            {'question': 'Which song\'s lyrics include "Chestnuts roasting on an open fire"?', 'options': ['The Christmas Song', 'Jingle Bells', 'Last Christmas', 'Silver Bells'], 'answer': 0},
            {'question': 'Which holiday film is set in the town of Bedford Falls?', 'options': ['It’s a Wonderful Life', 'Home Alone', 'A Christmas Carol', 'Miracle on 34th Street'], 'answer': 0},
            {'question': 'In "Four Christmases," what holiday tradition does the couple try to avoid?', 'options': ['Spending Christmas with their families', 'Decorating their house', 'Gift exchanges', 'Cooking holiday meals'], 'answer': 0},          
        ],
        'round_3': [
            {'question': 'In which country is it a tradition to eat KFC for Christmas dinner?', 'options': ['Japan', 'South Korea', 'China', 'Thailand'], 'answer': 0},
            {'question': 'What is the name of the Jewish holiday that is also known as the Festival of Lights?', 'options': ['Hanukkah', 'Passover', 'Yom Kippur', 'Rosh Hashanah'], 'answer': 0},
            {'question': 'In which country do people celebrate Christmas by roller skating to church?', 'options': ['Venezuela', 'Brazil', 'Argentina', 'Mexico'], 'answer': 0},
            {'question': 'What is the traditional Christmas Eve meal in Italy called?', 'options': ['Feast of the Seven Fishes', 'La Noche Buena', 'Réveillon', 'Wigilia'], 'answer': 0},
            {'question': 'Which country celebrates Christmas with a giant lantern festival?', 'options': ['Philippines', 'Indonesia', 'Malaysia', 'Vietnam'], 'answer': 0},
            {'question': 'In which country is it a tradition to hide all brooms on Christmas Eve?', 'options': ['Sweden', 'Finland', 'Norway', 'Denmark'], 'answer': 2},
            {'question': 'In "Jingle All the Way," who plays the character of Howard Langston?', 'options': ['Arnold Schwarzenegger', 'Chris Pratt', 'Tim Allen', 'Danny DeVito'], 'answer': 0},
            {'question': 'What is the name of the traditional Mexican Christmas celebration that includes a reenactment of Mary and Joseph\'s search for shelter?', 'options': ['Las Posadas', 'La Navidad', 'El Día de los Reyes', 'La Fiesta de Guadalupe'], 'answer': 0},
            {'question': 'In which country is it a tradition to eat 12 grapes at midnight on New Year\'s Eve?', 'options': ['Portugal','Spain', 'Italy', 'Greece'], 'answer': 1},
            {'question': 'What is the name of the traditional German Christmas market?', 'options': ['Christkindlmarkt', 'Weihnachtsmarkt', 'Nikolausmarkt', 'Adventsmarkt'], 'answer': 0},
            {'question': 'In which country is it a tradition to celebrate Christmas with a witch named La Befana?', 'options': ['Italy', 'France', 'Spain', 'Greece'], 'answer': 0},
            {'question': 'Which holiday is celebrated on the 5th of December in the Netherlands?', 'options': ['Sinterklaas', 'Christmas', 'Hanukkah', 'Diwali'], 'answer': 0},
            {'question': 'What is the traditional Christmas dessert in the UK?', 'options': ['Christmas Pudding', 'Fruitcake', 'Gingerbread', 'Yule Log'], 'answer': 0},
            {'question': 'Which country is famous for the "Jólakötturinn" or "Yule Cat" during the Christmas season?', 'options': ['Iceland', 'Norway', 'Sweden', 'Finland'], 'answer': 0},
            {'question': 'In "The Polar Express," what is the first gift of Christmas?', 'options': ['A bell', 'A toy train', 'A snow globe', 'A teddy bear'], 'answer': 0},
            {'question': 'In *Futurama*, what holiday is celebrated in the episode "A Pharaoh to Remember"?', 'options': ['Christmas', 'Farnsworth Day', 'Robanukah', 'New Year’s Eve'], 'answer': 0},      
        ],
        'bonus': [
            {'question': 'In "The Muppet Christmas Carol," who plays Bob Cratchit?', 'options': ['Kermit the Frog', 'Fozzie Bear', 'Gonzo', 'Animal'], 'answer': 0},
            {'question': 'In "National Lampoon’s Christmas Vacation," what does Clark Griswold put on his house?', 'options': ['Christmas lights', 'A giant Santa', 'Inflatable snowman', 'Reindeer statues'], 'answer': 0},
            {'question': 'In "The Nightmare Before Christmas," who is the "Pumpkin King"?', 'options': ['Jack Skellington', 'Oogie Boogie', 'Sally', 'Zero'], 'answer': 0},
            {'question': 'In "Bad Santa," what is the name of the character played by Billy Bob Thornton?', 'options': ['Willie T. Soke', 'Santa Joe', 'Nick Claus', 'Big Bill'], 'answer': 0},
            {'question': 'In "Die Hard," what is the name of the skyscraper where the events take place?', 'options': ['Nakatomi Plaza', 'Regent Tower', 'Empire State Building', 'Willis Tower'], 'answer': 0},
            {'question': 'In "Batman Returns," who plays the character of Selina Kyle (Catwoman)?', 'options': ['Michelle Pfeiffer', 'Anne Hathaway', 'Halle Berry', 'Julie Newmar'], 'answer': 0},
            {'question': 'In "Four Christmases," who plays the role of Brad, the main character?', 'options': ['Vince Vaughn', 'Will Ferrell', 'Ben Stiller', 'Paul Rudd'], 'answer': 0},
            {'question': 'In "Jingle All the Way," what is the name of the toy that Howard Langston tries to buy for his son?', 'options': ['Turbo Man', 'Power Ranger', 'Action Hero', 'Super Soldier'], 'answer': 0},
            {'question': 'What is the best-selling Christmas song of all time?', 'options': ['White Christmas', 'Last Christmas', 'Jingle Bells', 'Silent Night'], 'answer': 0},
            {'question': 'In the *Seinfeld* episode "The Strike," what holiday does Kramer invent?', 'options': ['Festivus', 'Christmas in July', 'Winter Solstice', 'Kwanzaa'], 'answer': 0},
            {'question': 'In "Rudolph the Red-Nosed Reindeer," what is the name of Rudolph\'s elf friend who wants to be a dentist?', 'options': ['Hermey', 'Sam', 'Yukon', 'Clarice'], 'answer': 0},
            {'question': 'In *The Simpsons* episode "Simpsons Roasting on an Open Fire," what does Homer get for Christmas?', 'options': ['A tattoo', 'A credit card', 'A new car', 'A haircut'], 'answer': 0},
        ],
    }
}

@app.route('/general_holiday_trivia/game', methods=['GET', 'POST'])
def general_holiday_trivia_game():
    if request.method == 'POST':
        user_name = request.form.get('name', '').strip()
        if not user_name:  # Ensure name is provided
            return "Error: Name is required to start the game.", 400

        session['user_name'] = user_name
        session['score'] = 0  # Start with a score of 0
        return redirect(url_for('general_holiday_trivia_round_1'))
    
    # Render the form to collect the player's name
    return render_template('general_holiday_trivia/game.html')


@app.route('/general_holiday_trivia/round_1', methods=['GET', 'POST'])
def general_holiday_trivia_round_1():
    if 'user_name' not in session or 'score' not in session:
        return redirect(url_for('general_holiday_trivia_game'))  # Redirect to game start
    
    if request.method == 'POST':
        score = session.get('score', 0)
        questions_in_round = questions['general_holiday_trivia']['round_1']
        
        # Shuffle questions
        random.shuffle(questions_in_round)
        
        # Shuffle answer options and update the correct answer index
        for question in questions_in_round:
            options = question['options']
            correct_answer = question['answer']
            # Shuffle the options
            random.shuffle(options)
            # Update the answer index based on shuffled options
            question['answer'] = options.index(options[correct_answer])
        
        # Iterate over shuffled questions and check answers
        for i, question in enumerate(questions_in_round):
            answer = request.form.get(f'answer{i}')
            if answer and int(answer) == question['answer']:
                score += 1
        
        session['score'] = score
        return redirect(url_for('general_holiday_trivia_round_2'))
    
    # Shuffle the questions here before rendering
    questions_in_round = questions['general_holiday_trivia']['round_1']
    random.shuffle(questions_in_round)
    
    return render_template('general_holiday_trivia/round.html', round_number=1, questions=questions_in_round)

@app.route('/general_holiday_trivia/round_2', methods=['GET', 'POST'])
def general_holiday_trivia_round_2():
    if 'user_name' not in session or 'score' not in session:
        return redirect(url_for('general_holiday_trivia_game'))  # Redirect to game start
    
    if request.method == 'POST':
        score = session.get('score', 0)
        questions_in_round = questions['general_holiday_trivia']['round_2']
        
        # Shuffle questions
        random.shuffle(questions_in_round)
        
        # Shuffle answer options and update the correct answer index
        for question in questions_in_round:
            options = question['options']
            correct_answer = question['answer']
            # Shuffle the options
            random.shuffle(options)
            # Update the answer index based on shuffled options
            question['answer'] = options.index(options[correct_answer])
        
        # Iterate over shuffled questions and check answers
        for i, question in enumerate(questions_in_round):
            answer = request.form.get(f'answer{i}')
            if answer and int(answer) == question['answer']:
                score += 1
        
        session['score'] = score
        return redirect(url_for('general_holiday_trivia_round_3'))
    
    # Shuffle the questions here before rendering
    questions_in_round = questions['general_holiday_trivia']['round_2']
    random.shuffle(questions_in_round)
    
    return render_template('general_holiday_trivia/round.html', round_number=2, questions=questions_in_round)


@app.route('/general_holiday_trivia/round_3', methods=['GET', 'POST'])
def general_holiday_trivia_round_3():
    if 'user_name' not in session or 'score' not in session:
        return redirect(url_for('general_holiday_trivia_game'))  # Redirect to game start
    
    if request.method == 'POST':
        score = session.get('score', 0)
        questions_in_round = questions['general_holiday_trivia']['round_3']
        
        # Shuffle questions
        random.shuffle(questions_in_round)
        
        # Shuffle answer options and update the correct answer index
        for question in questions_in_round:
            options = question['options']
            correct_answer = question['answer']
            # Shuffle the options
            random.shuffle(options)
            # Update the answer index based on shuffled options
            question['answer'] = options.index(options[correct_answer])
        
        # Iterate over shuffled questions and check answers
        for i, question in enumerate(questions_in_round):
            answer = request.form.get(f'answer{i}')
            if answer and int(answer) == question['answer']:
                score += 1
        
        session['score'] = score
        return redirect(url_for('general_holiday_trivia_bonus'))
    
    # Shuffle the questions here before rendering
    questions_in_round = questions['general_holiday_trivia']['round_3']
    random.shuffle(questions_in_round)
    
    return render_template('general_holiday_trivia/round.html', round_number=3, questions=questions_in_round)



@app.route('/general_holiday_trivia/bonus', methods=['GET', 'POST'])
def general_holiday_trivia_bonus():
    if 'user_name' not in session or 'score' not in session:
        return redirect(url_for('general_holiday_trivia_game'))  # Redirect to game start
    
    if request.method == 'POST':
        score = session.get('score', 0)
        questions_in_round = questions['general_holiday_trivia']['bonus']
        
        # Shuffle questions
        random.shuffle(questions_in_round)
        
        # Shuffle answer options and update the correct answer index
        for question in questions_in_round:
            options = question['options']
            correct_answer = question['answer']
            # Shuffle the options
            random.shuffle(options)
            # Update the answer index based on shuffled options
            question['answer'] = options.index(options[correct_answer])
        
        # Iterate over shuffled questions and check answers
        for i, question in enumerate(questions_in_round):
            answer = request.form.get(f'answer{i}')
            if answer and int(answer) == question['answer']:
                score += 1
        
        session['score'] = score
        return redirect(url_for('general_holiday_trivia_game_over'))
    
    # Shuffle the questions here before rendering
    questions_in_round = questions['general_holiday_trivia']['bonus']
    random.shuffle(questions_in_round)
    
    return render_template('general_holiday_trivia/round.html', round_number='Bonus', questions=questions_in_round)


@app.route('/general_holiday_trivia/game_over', methods=['GET'])
def general_holiday_trivia_game_over():
    user_name = session.get('user_name', 'Guest')
    score = session.get('score', 0)

    # Store the score in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trivia_scores (user_name, score) VALUES (?, ?)", (user_name, score))
    conn.commit()
    conn.close()

    return render_template('general_holiday_trivia/game_over.html', user_name=user_name, score=score)

@app.route('/leaderboard_trivia')
def leaderboard_trivia():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch trivia scores
    cursor.execute("SELECT user_name, score FROM trivia_scores ORDER BY score DESC")
    leaderboard_data = [{"name": row[0], "score": row[1]} for row in cursor.fetchall()]
    conn.close()

    return render_template('leaderboard/leaderboard_trivia.html', leaderboard_data=leaderboard_data)

# Bingo Game Logic
bingo_prompts = [
    "Find someone who has traveled to another country this year.",
    "Find someone who can name all of Santa's reindeer.",
    "Find someone who has a holiday tradition that involves food.",
    "Find someone who has a pet.",
    "Find someone who has completed a certification or training this year?",
    "Find someone who has seen a holiday movie this week.",
    "Find someone who can sing a holiday song.",
    "Find someone who has a unique holiday decoration.",
    "Find someone who has baked holiday cookies this year already.",
    "Find someone who has a holiday sweater.",
    "Find someone who is wearing a Best Buy sweater.",
    "Find someone who is wearing a Best Buy Attire.",
    "Find someone who has a favorite holiday memory.",
    "Find someone who has a holiday playlist one spoify  or youtube they can share.",
    "Find someone who has a holiday-themed phone background.",
    "Find someone who has a holiday party planned to host.",
    "Find someone who has a holiday recipe to share.",
    "Find someone who loves holiday books.",
    "Find someone who has a holiday craft project.",
    "Find someone who has a holiday card collection.",
    "Find someone who has a holiday tradition involving games.",
    "Find someone who has a holiday-themed mug.",
    "Find someone who has a holiday-themed piece of clothing.",
    "Find someone who has a holiday-themed pet accessory.",
    "Find someone who has a holiday-themed piece of jewelry.",
    "Find someone who has a holiday-themed piece of art.",
    "Find someone who has a holiday-themed piece of home decor.",
    "Find someone who has a holiday-themed piece of technology.",
    "Find someone who has not worked through a Best Buy Holiday season.",
    "Find someone who has a worked through 1 Best Buy Holiday season.",
    "Find someone who has a worked through 5 Best Buy Holiday seasons.",
    "Find someone who has a worked through 10 Best Buy Holiday seasons.",
    "Find someone who has a worked through 15 Best Buy Holiday seasons.",
    "Find someone who has a worked through 20 Best Buy Holiday seasons.",
    "Find someone who has a worked through 25 Best Buy Holiday seasons."
]

def generate_bingo_card():
    card = random.sample(bingo_prompts, 25)  # Randomly select 25 prompts
    return [card[i:i+5] for i in range(0, 25, 5)]  # 5x5 grid

leaderboard_bingo = defaultdict(int)

bingo_leaderboard = defaultdict(int)  # Renamed the leaderboard variable

@app.route('/bingo/holiday_bingo', methods=['GET', 'POST'])
def holiday_bingo():
    if request.method == 'GET':
        # Generate a new card if one isn't already in session
        bingo_card = generate_bingo_card()
        session['bingo_card'] = bingo_card
        session['submitted_cards'] = session.get('submitted_cards', 0)  # Track submitted cards

        return render_template(
            'bingo/holiday_bingo.html',
            bingo_card=bingo_card
        )

    elif request.method == 'POST':
        user_name = request.form.get('name', '').strip().lower()  # Case-insensitive user names
        if not user_name:
            return "Error: Name is required.", 400

        # Ensure the leaderboard tracks submissions for each user
        if "bingo_submissions" not in session:
            session["bingo_submissions"] = {}

        user_submissions = session["bingo_submissions"].get(user_name, 0)

        # Check if the user has already submitted two cards
        if user_submissions >= 2:
            return f"Error: You have already submitted the maximum of 2 bingo cards under the name '{user_name}' .", 400

        bingo_card = session.get('bingo_card', [])
        used_names = set()  # To ensure unique non-empty names per card

        # Validate and process form input
        for i in range(5):
            for j in range(5):
                square_name = f"square_{i}_{j}"
                if square_name in request.form:
                    name_input = request.form[square_name].strip().lower()
                    if name_input:  # Only check non-empty names for uniqueness
                        if name_input in used_names:
                            return f"Error: The name '{name_input}' has already been used in a square on this card. Names can only be used once per square", 400
                        used_names.add(name_input)  # Add to the set of used names
                    bingo_card[i][j] = name_input  # Save name (or empty) to card

        session['bingo_card'] = bingo_card  # Save the updated card

        # Check for Bingo and calculate the score
        score = check_for_bingo(bingo_card)
        bingo_leaderboard[user_name] += score  # Increment score in leaderboard

        # Increment the user's submission count
        session["bingo_submissions"][user_name] = user_submissions + 1

        return redirect(url_for('leaderboard_bingo'))


def check_for_bingo(bingo_card):
    """
    Check the bingo card for valid rows, columns, and diagonals.
    Each line is worth 1 point, with a maximum of 12 points possible.
    """
    score = 0

    # Check rows and columns
    for i in range(5):
        if all(bingo_card[i][j] for j in range(5)):  # Row bingo
            score += 1
        if all(bingo_card[j][i] for j in range(5)):  # Column bingo
            score += 1

    # Check diagonals
    if all(bingo_card[i][i] for i in range(5)):  # Main diagonal
        score += 1
    if all(bingo_card[i][4 - i] for i in range(5)):  # Anti-diagonal
        score += 1

    return score


@app.route('/bingo/reset', methods=['POST'])
def reset_bingo():
    # Remove the 'bingo_card' from the session if it exists
    session.pop('bingo_card', None)
    
    # Redirect the user to the 'holiday_bingo' route
    return redirect(url_for('holiday_bingo'))



@app.route('/leaderboard_bingo', methods=['GET'])
def leaderboard_bingo():
    # Sort leaderboard by score in descending order
    sorted_leaderboard = dict(sorted(bingo_leaderboard.items(), key=lambda x: x[1], reverse=True))
    return render_template('/leaderboard/leaderboard_bingo.html', leaderboard=sorted_leaderboard)


def check_for_bingo(bingo_card):
    score = 0
    # Check rows and columns for Bingo
    for i in range(5):
        if all(bingo_card[i][j] for j in range(5)):  # Check row
            score += 1
        if all(bingo_card[j][i] for j in range(5)):  # Check column
            score += 1

    # Check diagonals for Bingo
    if all(bingo_card[i][i] for i in range(5)):  # Check main diagonal
        score += 1
    if all(bingo_card[i][4-i] for i in range(5)):  # Check anti-diagonal
        score += 1

    return score

# This function would need to be called when the user gets Bingo:
def update_bingo_score(user_name):
    if user_name in leaderboard_bingo:
        leaderboard_bingo[user_name] += 1  # Increment score
    else:
        leaderboard_bingo[user_name] = 1  # Set initial score


@app.route('/bingo/rules', methods=['GET'])
def bingo_rules():
    return render_template('bingo/bingo_rules.html')

# leadership trivia
leaders = ["Russ", "Sampson", "Nate", "Matt", "Scott P", "Scott S", "Lynda", "Todd", "Jess"]

leadership_questions = [
    {"question": "Which leader grew up in a town smaller than the BBY corp campus population (pre-COVID days)?", "answer": "Russ"},
    {"question": "Which leader has visited 42 of the 50 United States?", "answer": "Nate"},
    {"question": "Which leader has been in a commercial plane crash?", "answer": "Matt"},
    {"question": "Which leader coached 3 state youth basketball championships in a span of 5 years", "answer" :"Russ"},
    {"question": "Which leader has had 3 kids attended or attending Kansas University? - GO Jayhawks!!", "answer": "Russ"},
    {"question": "Which leader attended the University of North Dakota (Fighting Sioux)", "answer": "Nate"},
    {"question": "Which leader has played or coached baseball for for over 40 years combinded?", "answer": "Nate"},
    {"question": "Which leader shares the same wedding anniversary date (August 19) with both their parents and in-laws", "answer": "Nate"},
    {"question": "Which leader has lived in Minnesota for most of their life yet is a Green Bay Packers football fan", "answer": "Nate"},
    {"question": "Which leader was born and grew up in MN, but went to high school in Arizona, college in St. Cloud, and lived in New York", "answer": "Matt"},
    {"question": "Which leader's family has hosted 5 different international students when their kids were in high school", "answer": "Matt"},
    {"question": "Which leader has kids at two different University of Minnesota colleges currently", "answer": "Matt" },
    {"question": "Which leader was born out side of the United States", "answer": "Sampson"},
    {"question": "Which leader has Skied down the highest the chairlift in North America, topping out at an elevation of 12,840 feet", "answer": "Sampson"},
    {"question": "Which leader shares a Decemeber birthday with Actors, Adam Brody and Don Johnson", "answer": "Sampson"},
    {"question": "Which leader has had multiple traumatic fishing trips as a child, which has turned them off fishing forever", "answer": "Todd"},
    {"question": "Which leader went to a school that had less than 300 students in both middle and high(7-12) school combined", "answer": "Todd"},
    {"question": "Which leader's vision has only improved as they've gotten older", "answer": "Todd"},
    {"question": "Which leader starded working for Best Buy in November 1990", "answer": "Todd"},
    {"question": "Which leader had their house taken over for a night by a SWAT team", "answer": "Todd"}
]

@app.route('/leadership_trivia/setup', methods=['GET', 'POST'])
def leadership_trivia_setup():
    if request.method == 'POST':
        user_name = request.form.get('name', '').strip()
        num_questions = int(request.form.get('num_questions', 10))
        predicted_score = int(request.form.get('predicted_score', 0))

        # Check if user has already played this question count
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM leadership_scores 
            WHERE user_name = ? AND questions_count = ?
        """, (user_name, num_questions))
        if cursor.fetchone():
            return "You have already played this version of the game. Please choose a different number of questions.", 400

        # Save setup info to session
        session['user_name'] = user_name
        session['num_questions'] = num_questions
        session['predicted_score'] = predicted_score
        session['actual_score'] = 0
        session['current_question_index'] = 0

        # Randomize questions and store them in session
        randomized_questions = random.sample(leadership_questions, k=min(len(leadership_questions), num_questions))
        session['questions'] = randomized_questions

        return redirect(url_for('leadership_trivia_question'))

    return render_template('leadership_trivia/setup.html')


@app.route('/leadership_trivia/question', methods=['GET', 'POST'])
def leadership_trivia_question():
    # If user finished all questions, redirect to results
    if 'questions' not in session or session['current_question_index'] >= session['num_questions']:
        return redirect(url_for('leadership_trivia_results'))

    if request.method == 'POST':
        selected_answer = request.form.get('selected_leader', '')
        current_question = session['questions'][session['current_question_index']]
        correct_answer = current_question['answer']

        # Check correctness and update score
        is_correct = selected_answer == correct_answer
        if is_correct:
            session['actual_score'] += 1

        # Store feedback information in session
        session['feedback'] = {
            'question': current_question,
            'selected_answer': selected_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        }

        # Show feedback before proceeding
        return redirect(url_for('leadership_trivia_feedback'))

    # Display the current question
    current_question = session['questions'][session['current_question_index']]
    randomized_leaders = random.sample(leaders, k=4)
    if current_question['answer'] not in randomized_leaders:
        randomized_leaders[0] = current_question['answer']
        random.shuffle(randomized_leaders)

    return render_template('leadership_trivia/question.html', question=current_question, leaders=randomized_leaders)


@app.route('/leadership_trivia/feedback', methods=['GET', 'POST'])
def leadership_trivia_feedback():
    # If there's no feedback, redirect back to the question
    if 'feedback' not in session:
        return redirect(url_for('leadership_trivia_question'))

    feedback = session['feedback']

    if request.method == 'POST':
        # Clear feedback and move to the next question
        session.pop('feedback', None)
        session['current_question_index'] += 1
        return redirect(url_for('leadership_trivia_question'))

    return render_template(
        'leadership_trivia/answer_feedback.html',
        question=feedback['question'],
        selected_answer=feedback['selected_answer'],
        correct_answer=feedback['correct_answer'],
        is_correct=feedback['is_correct']
    )



@app.route('/leadership_trivia/results')
def leadership_trivia_results():
    user_name = session.get('user_name', 'Guest')
    num_questions = session.get('num_questions', 0)
    predicted_score = session.get('predicted_score', 0)
    actual_score = session.get('actual_score', 0)

    # Save to database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leadership_scores (user_name, questions_count, predicted_score, actual_score)
        VALUES (?, ?, ?, ?)
    """, (user_name, num_questions, predicted_score, actual_score))
    conn.commit()
    conn.close()

    return render_template('leadership_trivia/results.html', user_name=user_name, num_questions=num_questions, predicted_score=predicted_score, actual_score=actual_score)

@app.route('/leaderboard_leadership_trivia')
def leaderboard_leadership_trivia():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_name, questions_count, predicted_score, actual_score 
        FROM leadership_scores
    """)
    results = cursor.fetchall()
    conn.close()

    # Calculate composite scores for leaderboard
    leaderboard_data = []
    for row in results:
        questions_attempted = row['questions_count']
        predicted_score = row['predicted_score']
        actual_score = row['actual_score']

        # Use scoring algorithm
        accuracy_score = 1 - abs(predicted_score - actual_score) / questions_attempted
        accuracy_score = max(0, accuracy_score)  # Ensure non-negative
        performance_score = (actual_score / questions_attempted) * questions_attempted
        composite_score = (accuracy_score * 0.4) + (performance_score * 0.6)

        leaderboard_data.append({
            "user_name": row['user_name'],
            "questions_attempted": questions_attempted,
            "predicted_score": predicted_score,
            "actual_score": actual_score,
            "composite_score": composite_score
        })

    # Sort by composite score descending
    leaderboard_data = sorted(leaderboard_data, key=lambda x: x['composite_score'], reverse=True)

    return render_template('leaderboard/leaderboard_leadership_trivia.html', leaderboard_data=leaderboard_data)

@app.route('/leadership_trivia/rules', methods=['GET'])
def leadership_trivia_rules():
    return render_template('leadership_trivia/rules.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
import csv
from src.datatypes import Character, Movie, Conversation, Line
import os
import io
from supabase import Client, create_client
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

# Reading in the log file from the supabase bucket
log_csv = (
    supabase.storage.from_("movie-api")
    .download("movie_conversations_log.csv")
    .decode("utf-8")
)

logs = []
for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
    logs.append(row)


# Writing to the log file and uploading to the supabase bucket
def upload_new_log():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["post_call_time", "movie_id_added_to"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(logs)
    supabase.storage.from_("movie-api").upload(
        "movie_conversations_log.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )


# END PLACEHOLDER CODE


def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None

class movie:

    def __init__(self, movie_id: int, title: str, year: int, imdb_rating: float, imdb_votes: int, raw_script_url: str):
        self.movie_id  = movie_id
        self.title = title
        self.year = year
        self.imdb_rating = imdb_rating
        self.imdb_votes = imdb_votes
        self.raw_script_url = raw_script_url

class character:

    def __init__(self, character_id: int, name: str, movie_id: int, gender: str, age: int):
        self.character_id = character_id
        self.name = (name or None)
        self.movie_id = movie_id
        self.gender = (gender or None)
        self.age = age
        self.lines = 0      # integer to count the amount of lines within the movie

class conversation:

    def __init__(self, conversation_id: int, character1_id: int, character2_id: int, movie_id: int):
        self.conversation_id = conversation_id
        self.character1_id = character1_id
        self.character2_id = character2_id
        self.movie_id = movie_id
        self.lineCount = 0      # line count is initially zero to be added later
        self.character1_lines = 0
        self.character2_lines = 0

class line:

    def __init__(self, line_id: int, character_id: int, movie_id: int, conversation_id: int, line_sort: int, line_text: str):
        self.line_id = line_id
        self.character_id = character_id
        self.movie_id = movie_id
        self.conversation_id = conversation_id
        self.line_sort = line_sort
        self.line_text = line_text

# different than (val or None) because if val = 0, it would return None
def typeCheck(type, val):
    try: 
        return type(val)
    except ValueError:
        return None

class db:
    

    lines = {}
    with open("lines.csv", mode="r", encoding="utf8") as csv_file:
        for row in csv.DictReader(csv_file, skipinitialspace=True):
            cur = line(typeCheck(int, row['line_id']), typeCheck(int,row['character_id']), typeCheck(int, row['movie_id']), typeCheck(int, row['conversation_id']), typeCheck(int, row['line_sort']), str(row['line_text']))
            lines[cur.line_id] = cur

    conversations = {}
    with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
        for row in csv.DictReader(csv_file, skipinitialspace=True):
            cur = conversation(typeCheck(int, row['conversation_id']), typeCheck(int, row['character1_id']), typeCheck(int, row['character2_id']), typeCheck(int, row['movie_id']))
            conversations[cur.conversation_id] = cur

    movies = {}
    with open("movies.csv", mode="r", encoding="utf8") as csv_file:
        for row in csv.DictReader(csv_file, skipinitialspace=True):
            cur = movie(typeCheck(int, row['movie_id']), str(row['title']), str(row['year']), typeCheck(float, row['imdb_rating']), typeCheck(int, row['imdb_votes']), str(row['raw_script_url']))
            movies[cur.movie_id] = cur

    characters = {}
    charNames = {}
    with open("characters.csv", mode="r", encoding="utf8") as csv_file:
        for row in csv.DictReader(csv_file, skipinitialspace=True):
            cur = character(typeCheck(int, row['character_id']), str(row['name']), typeCheck(int, row['movie_id']), str(row['gender']), str(row['age']))
            characters[cur.character_id] = cur
            charNames[cur.name] = cur.character_id

    # calculating line count 
    for line in lines.values():

        # adding the conversation count
        conversations[line.conversation_id].lineCount += 1
        
        if line.character_id == conversations[line.conversation_id].character1_id:
            conversations[line.conversation_id].character1_lines += 1
        else:
            conversations[line.conversation_id].character2_lines += 1

        # adding the lines per character
        characters[line.character_id].lines += 1

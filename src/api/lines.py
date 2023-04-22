from fastapi import APIRouter, HTTPException
from enum import Enum 
from src import database as db
from typing import *

router = APIRouter()

# creating the database object 
data = db.db()

"""
functions for lines.py
list conversation -> display all of the lines of a conversation 
write out the first line of each conversation character is part of (searched by character name)

"""

@router.get("/lines/{conversation_id}", tags=["lines"])
def get_lines(conversation_id: int):
    """
    This endpoint returns the lines of a conversation based on its id. For each conversation, the endpoint returns
    * 'conversation_id': the conversation id of your desired conversation
    * 'title': the title of the movie the conversation is from
    * 'lines': a list of lines in the given conversation, sorted in order of line_sort
    
    Each line is represented with the following keys
    * 'name': the name of the character who said the line
    * 'line_text': the text of the line
    
    """

    json = None

    if conversation_id in data.conversations:

        lines = [(line, data.characters[line.character_id].name) for line in data.lines.values() if conversation_id == line.conversation_id]

        # sort for outputting
        lines = sorted(lines, key=lambda x: x[0].line_sort)

        lineJson = [{
            "name": line[1],
            "line_text": line[0].line_text
        } for line in lines]

        json = {
            "conversation_id": conversation_id,
            "title": data.movies[data.conversations[conversation_id].movie_id].title,
            "lines": lineJson
        }

        if json is None:
            raise HTTPException(status_code=404, detail="conversation not found.")
        
        return json
    
@router.get("/lines/names/{name}", tags=["lines"])
def get_character_convos(name: str):
    """
    This endpoint returns a list of characters that match the given name. For each character, the endpoint returns:
    * 'name': The character's name
    * 'character_id': character id 
    * 'conversation count': amount of conversations the character is in
    * 'conversations': a list of conversations the character is in, sorted by conversation id

    Each conversation identifier is represented by a dictionary with the following keys:
    * 'title': Movie title the character is in
    * 'line_count': how many lines the character had in the conversation
    * 'other_charcter': the name of the other character they are talking to
    """
    jsons = []

    name = name.upper()     # turn the name into all caps in order to match the datab

    if name in data.charNames:
        for id in data.charNames[name]:
            convos = [] #[convo for convo in data.conversations.values() if convo.character1_id == id or convo.character2_id == id]

            # convo to keep only one of each conversation
            c = {}
            for convo in data.conversations.values():
                if (convo.character1_id == id or convo.character2_id == id) and convo.conversation_id not in c:
                    convos.append(convo)
            
            convos = sorted(convos, key=lambda x: x.conversation_id)

            convosJson = []

            for convo in convos:
                if id == convo.character1_id:
                    count = convo.character1_lines
                    other = data.characters[convo.character2_id].name
                else:
                    count = convo.character2_lines
                    other = data.characters[convo.character1_id].name

                convosJson.append({
                    "title": data.movies[convo.movie_id].title,
                    "line_count": count,
                    "other_character": other
                }) 

            json ={
                "name": name,
                "character_id": id,
                "conversation_count": len(convos),
                "conversations": convosJson
            }
            jsons.append(json)
    
    # this means that the name was not found
    if jsons == []:
        raise HTTPException(status_code=404, detail="character not found.")

    return jsons

class conversation_sort_options(str, Enum):
    line_count = "line_count"
    title = "title"
    conversation_id = "conversation_id"

@router.get("/lines/conversations/", tags=["lines"])
def list_conversations(
    count: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    sort: conversation_sort_options = conversation_sort_options.conversation_id
):
    """
    This endpoint returns a list of conversations. For each conversation it returns:
    * 'conversation_id': the internal id of the  conversation
    * 'title': title of the movie it is from
    * 'character1': character1's name
    * 'character2': character2's name
    * 'line_count': line count for conversation

    You can filter for conversations whose conversations only meet the lineCount
    threshold

    You can sort the results by using the 'sort' query parameter:
    * 'line_count' - Sort based on line count, descending
    * 'title' - alphabetically sorted 
    * 'conversation_id' sorted based on conversation id's
    """

    if count:
        convos = [convo for convo in data.conversations.values() if convo.lineCount >= count]
    else:
        convos = [convo for convo in data.conversations.values()]

    if sort == conversation_sort_options.line_count:
        convos = sorted(convos, key=lambda x: x.lineCount, reverse=True)
    elif sort == conversation_sort_options.title:
        convos = sorted(convos, key = lambda x: data.movies[x.movie_id].title)
    elif sort == conversation_sort_options.conversation_id:
        convos = sorted(convos, key=lambda x: x.conversation_id)

    json = []

    # TODO: make sure it doesn't go more than the list

    for convo in convos[offset:offset + limit]:
        convoJson = {
            "conversation_id": convo.conversation_id,
            "title": data.movies[convo.movie_id].title,
            "character1": data.characters[convo.character1_id].name,
            "character2": data.characters[convo.character2_id].name,
            "line_count": convo.lineCount
        }
        json.append(convoJson)


    # for i in range(offset, limit + offset):
    #     convoJson = {
    #         "conversation_id": convos[i].conversation_id,
    #         "title": data.movies[convos[i].movie_id].title,
    #         "character1": data.characters[convos[i].character1_id].name,
    #         "character2": data.characters[convos[i].character2_id].name,
    #         "line_count": convos[i].lineCount
    #     }
    #     json.append(convoJson)

    return json

#@router.get("/characters/{id}", tags=["characters"])


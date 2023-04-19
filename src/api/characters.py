from collections import defaultdict
from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db

router = APIRouter()

# creating the database object
data = db.db()

# print the line count for conversation 
# print(data.conversations['189'].lineCount)


def get_top_conv_characters(character):
    c_id = character.id
    movie_id = character.movie_id
    all_convs = filter(
        lambda conv: conv.movie_id == movie_id
        and (conv.c1_id == c_id or conv.c2_id == c_id),
        db.conversations.values(),
    )
    line_counts = Counter()

    for conv in all_convs:
        other_id = conv.c2_id if conv.c1_id == c_id else conv.c1_id
        line_counts[other_id] += conv.num_lines

    return line_counts.most_common()


@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """
    json = None
    # print(data.characters)


    # remove this just lookup in the dictionary
    # if character exists
    if id in data.characters:
        print("character found")
        character = data.characters[id]

        """
        convo_json strats:

        traverse the conversations
          for each conversation, we traverse the lines file to calculate the amount of lines & such
        """
        
        convos = defaultdict(int)
        convosJson = []

        # for the character, traverse through the conversations and add the convo object if the have a convo
        # sort them based on the conversation lineCount
        for convo in data.conversations.values():
            if convo.character1_id == character.character_id:
                # add the object based on the second character
                convos[convo.character2_id] += convo.lineCount
            elif convo.character2_id == character.character_id:
                convos[convo.character1_id] += convo.lineCount
        convosSorted = sorted(convos.items(), key=lambda x: x[1], reverse=True)

        # after the list is made, turn them all into json's for the return statement
        for convo in convosSorted:
            
            convoJson = {
                "character_id": convo[0],
                "character": data.characters[convo[0]].name,
                "gender": data.characters[convo[0]].gender,
                "number_of_lines_together": convo[1]
            }
            convosJson.append(convoJson)

        # building the actual character json
        json = {
            "character_id": character.character_id,
            "character": character.name,
            "movie": data.movies[character.movie_id].title,
            "gender": character.gender,
            "top_conversations": convosJson
          }
    if json is None:
        raise HTTPException(status_code=404, detail="character not found.")
    return json


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    # filter out
    if name != "":
      charList = [character for character in data.characters.values() if name.upper() in character.name]
    else:
      charList = [character for character in data.characters.values() if character.name is not None]
        
    # in order to preprocess the number of lines, I am going to have one pass through the 
    if sort == character_sort_options.character:
        charList = sorted(charList, key=lambda x: x.name)
        
        
    elif sort == character_sort_options.movie:
        charList = sorted(charList, key=lambda x: x.movie)

    elif sort == character_sort_options.number_of_lines:
        charList = sorted(charList, key=lambda x: x.lines, reverse=True)

    json = []

    # making sure the limit isn't too high
    if limit > len(charList):
        limit = len(charList)


    for character in charList[offset: offset + limit]:
        characterJson = {
            "character_id": character.character_id,
            "character": character.name,
            "movie": data.movies[character.movie_id].title,
            "number_of_lines": character.lines
        }
        json.append(characterJson)

    # for i in range(offset, offset + limit):
    #     characterJson = {
    #         "character_id": charList[i].character_id,
    #         "character": charList[i].name,
    #         "movie": data.movies[charList[i].movie_id].title,
    #         "number_of_lines": charList[i].lines
    #     }
    #     json.append(characterJson)
    return json

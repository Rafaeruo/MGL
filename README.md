# MGL - MyGameList

Practice project I made when I was first learning about web APIs and backend development using Python and Flask.

This uses the [IGDB API](https://api-docs.igdb.com/) to fetch game data.

# Requirements

PIP dependencies are listed in `requirements.txt`.
For the API communication to work, the following environment variables are required:

| Key            |
| -------------- | 
| AUTHORIZATION  | 
| CLIENT_ID      | 
| CLIENT_SECRET  | 

Refer to the [Official IGDB API docs](https://api-docs.igdb.com/) for instructions on how to acquire them.

Oher than that, don't forget to set the `FLASK_APP` envronment variable to `application.py`, so that Flask knows what to run.

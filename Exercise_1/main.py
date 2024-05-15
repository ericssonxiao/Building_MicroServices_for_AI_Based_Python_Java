import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import databases
import sqlalchemy
from sqlalchemy import create_engine, text
# Database connection URL
# In the file of docker-compose.yml, config: DATABASE_URL=postgresql://user:password@db:5432/notes
# When run at local system for development, use this: DATABASE_URL = "postgresql://postgres:psql123456@localhost:5432/notes"
# When need to publish on docker, use this configuration: DATABASE_URL = "postgresql://user:password@host:port/database"
DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
database = databases.Database(DATABASE_URL)

# SQLAlchemy metadata
metadata = sqlalchemy.MetaData()

# Define database table
notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("content", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean),
)

# Create the table if it doesn't exist
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

# Pydantic model
class NoteIn(BaseModel):
    title: str
    content: str
    completed: bool

# Pydantic model
class NoteOut(BaseModel):
    id:int
    title: str
    content: str
    completed: bool

# FastAPI app
app = FastAPI()

# Connect to the database on startup
@app.on_event("startup")
async def startup():
    await database.connect()

# Disconnect from the database on shutdown
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Create a new note
@app.post("/notes/", response_model=NoteIn)
async def create_note(note: NoteIn):
    query = notes.insert().values(title=note.title, content=note.content, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}

# Update a note
@app.put("/notes/{note_id}", response_model=NoteIn)
async def update_note(note_id: int, note: NoteIn):
    query = notes.update().where(notes.c.id == note_id).values(title=note.title, content=note.content, completed=note.completed)
    await database.execute(query)
    return {**note.dict(), "id": note_id,"test":"Hello!"}

# Get all notes
@app.get("/notes/", response_model=list[NoteOut])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)

# Get a single one note
@app.get("/notes/{note_id}", response_model=NoteOut)
async def getNote(note_id: int):
    query = notes.select().where(notes.c.id == note_id)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Note not found.")
    return NoteOut.parse_obj(result)


# Run the app with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
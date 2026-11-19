
from fastapi import FastAPI, HTTPException, Query

from pydantic import BaseModel, Field

from pathlib import Path

import json

app = FastAPI()

FILE_PATH = Path(__file__).with_name("notes.json")


def save_notes():
    with open(FILE_PATH, "w") as file:
        json.dump(notes, file, indent=4)


def load_notes():

    if FILE_PATH.exists():
        with open(FILE_PATH, "r") as file:
            return json.load(file)

    return [
        {"id": 1, "title": "Python Basics", "content": "Learning Python programming"},

        {"id": 2, "title": "FastAPI", "content": "Learning FastAPI fundamentals"},
        
        {"id": 3, "title": "HTML Basics", "content": "Learning HTML"}
    ]


notes = load_notes()

if not FILE_PATH.exists():
    save_notes()


class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    content: str = Field(min_length=5, max_length=500)


class NoteUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    content: str = Field(min_length=5, max_length=500)


@app.get("/")
def home():
    return {
        "message": "Welcome to Notes Management API"
    }


@app.get("/notes")
def get_notes():
    return notes


@app.get("/notes/search/{title}")
def search_note(title: str):

    for note in notes:
        if note["title"].lower() == title.lower():
            return note

    raise HTTPException(status_code=404, detail="Note not found")


@app.get("/notes/keyword/{keyword}")
def search_by_keyword(keyword: str):

    result = []

    for note in notes:
        if keyword.lower() in note["title"].lower() or keyword.lower() in note["content"].lower():
            result.append(note)

    if not result:
        raise HTTPException(status_code=404, detail="No matching notes found")

    return result


@app.get("/notes/filter")
def filter_notes(ids: list[int] = Query(...)):

    result = []

    for note in notes:
        if note["id"] in ids:
            result.append(note)

    if not result:
        raise HTTPException(status_code=404, detail="No matching notes found")

    return result


@app.get("/notes/sort")
def sort_notes(order: str = Query("asc", pattern="^(asc|desc)$")):

    if order == "asc":
        result = sorted(notes, key=lambda note: note["title"].lower())
    else:
        result = sorted(notes, key=lambda note: note["title"].lower(), reverse=True)

    return result


@app.get("/notes/statistics")
def notes_statistics():

    total_notes = len(notes)

    if total_notes == 0:
        return {
            "total_notes": 0,
            "highest_id": None,
            "lowest_id": None,
            "total_title_characters": 0,
            "total_content_characters": 0
        }

    return {
        "total_notes": total_notes,
        "highest_id": max(note["id"] for note in notes),
        "lowest_id": min(note["id"] for note in notes),
        "total_title_characters": sum(len(note["title"]) for note in notes),
        "total_content_characters": sum(len(note["content"]) for note in notes)
    }


@app.get("/notes/{note_id}")
def get_note_by_id(note_id: int):

    for note in notes:
        if note["id"] == note_id:
            return note

    raise HTTPException(status_code=404, detail="Note not found")


@app.post("/notes")
def create_note(note: NoteCreate):

    new_note = {
        "id": max([n["id"] for n in notes], default=0) + 1,
        "title": note.title,
        "content": note.content
    }

    notes.append(new_note)
    save_notes()

    return {
        "message": "Note created successfully!",
        "note": new_note
    }


@app.put("/notes/{note_id}")
def update_note(note_id: int, updated_data: NoteUpdate):

    for note in notes:
        if note["id"] == note_id:
            note["title"] = updated_data.title
            note["content"] = updated_data.content

            save_notes()

            return {
                "message": "Note Updated Successfully",
                "note": note
            }

    raise HTTPException(status_code=404, detail="Note not found!")


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):

    for note in notes:
        if note["id"] == note_id:
            notes.remove(note)
            save_notes()

            return {
                "message": "Note Deleted Successfully",
                "note": note
            }

    raise HTTPException(status_code=404, detail="Notes Not Found")

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import traceback
from pydantic import BaseModel
from ttt.chat import table_chat, error_chat
from ttt.validate import validate_csv
from ttt.utils import convert_string_to_datestring
import uuid
import duckdb
import json
import os


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tables = {}


class ChatRequest(BaseModel):
    talk_input: str
    session: str


@app.get("/hello")
async def root():
    return {"message": "Hello World"}


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    print("POST /upload")

    #cwd = os.getcwd()
    #print(cwd)
    #try:
    #    file_size = os.stat(cwd)
    #    print(file_size.st_size)
    #except FileNotFoundError:
    #    print("File not found.")

    session = None

    try:
        # with open(file.filename, 'wb') as f:
        # while contents := file.file.read(1024 * 1024):
        #     f.write(contents)
        table = pd.read_csv(file.file, header=0)
        table = validate_csv(table)
        session = str(uuid.uuid4())
        tables[session] = table
        tabledata = table.to_json(orient="records")
    except ValueError as e:
        raise HTTPException(
            status_code=422, detail=e.args[0]
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="There was a problem uploading your file"
        )
    finally:
        file.file.close()

    print(tabledata)
    return {
        "message": f"Successfully uploaded {file.filename}",
        "table": tabledata,
        "session": session,
    }


@app.post("/chat")
def do_chat(chat_request: ChatRequest):
    print("POST /chat")

    print(chat_request)

    try:
        current_df = tables.get(chat_request.session)

        response = table_chat(chat_request.talk_input, current_df)
        response_json = json.loads(response)

        print(response_json)

        if response_json.get("sql"):
            response_df = duckdb.query(response_json.get("sql")).df()
    except Exception:
        traceback.print_exc()
        exception_summary = traceback.format_exc()
        text_response = error_chat(exception_summary)
        raise HTTPException(
            status_code=500, detail=text_response
        )

    #response_df = response_df.applymap(convert_string_to_datestring) 
    return {"message": response, "table": response_df.to_json(orient="records")}

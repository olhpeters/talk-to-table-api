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
from datetime import datetime, timedelta

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
sessions = {}
MAX_ROWS = 10000


class ChatRequest(BaseModel):
    talk_input: str
    session: str


def session_check():
    sessions_to_delete = []
    for session_key, session in sessions.items():
        create_time = session["create_time"]
        now_time = datetime.now()
        if (now_time - timedelta(hours=1)) > create_time:
            # del sessions[session_key]
            sessions_to_delete.append(session_key)

    for session_key in sessions_to_delete:
        del sessions[session_key]
        print(f"clearing session {session_key}")

    print(f"total sessions {len(sessions)}")
    if len(sessions) > 5:
        raise ValueError(
            f"Sorry there is too much activity right now. Talk to Table is still in a prototype (alpha test) state and only allows a limited number of sessions (file uploads) an hour."
        )

def session_increment_chatcount(session):
    current_chat_count = session.get("chat_count")
    if current_chat_count > 5:
        raise ValueError(
            f"Sorry, Talk to Table is still in a prototype (alpha test) state and only allows a limited number of chats for each session (file)."
        )
    session["chat_count"] = current_chat_count + 1

@app.get("/")
async def root():
    return {"message": "Server is running"}


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    print("POST /upload")

    session = None

    try:
        # with open(file.filename, 'wb') as f:
        # while contents := file.file.read(1024 * 1024):
        #     f.write(contents)
        session_check()
        table = pd.read_csv(file.file, header=0, skipinitialspace=True, nrows=MAX_ROWS, on_bad_lines='skip', encoding_errors='ignore', sep=None)
        table = validate_csv(table)
        session = str(uuid.uuid4())
        # tables[session] = table
        sessions[session] = {
            "table": table,
            "create_time": datetime.now(),
            "chat_count": 0,
        }
        tabledata = table.to_json(orient="records")
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=e.args[0])
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="There was a problem uploading your file"
        )
    finally:
        file.file.close()

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
        current_session = sessions.get(chat_request.session)
        session_increment_chatcount(current_session)
        current_df = current_session.get("table")

        response = table_chat(chat_request.talk_input, current_df)
        response_json = json.loads(response)

        print(response_json)

        if response_json.get("sql"):
            response_df = duckdb.query(response_json.get("sql")).df()

    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=e.args[0])
    
    except Exception:
        traceback.print_exc()
        exception_summary = traceback.format_exc()
        text_response = error_chat(exception_summary)
        raise HTTPException(status_code=500, detail=text_response)

    # response_df = response_df.applymap(convert_string_to_datestring)
    return {"message": response, "table": response_df.to_json(orient="records")}


@app.post("/revert")
def revert(chat_request: ChatRequest):
    print("POST /revert")

    try:
        current_session = sessions.get(chat_request.session)
        current_df = current_session.get("table")
        tabledata = current_df.to_json(orient="records")
    except ValueError as e:
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=e.args[0])
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail="There was a problem reverting to your original file"
        )
    return {
        "message": f"Successfully reverted table",
        "table": tabledata,
    }

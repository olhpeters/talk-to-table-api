from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import traceback
from pydantic import BaseModel
from ttt.chat import chat


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    talk_input: str

@app.get("/hello")
async def root():
    return {"message": "Hello World"}
        
@app.post("/upload")
def upload(file: UploadFile = File(...)):

    print("POST /upload")
    tabledata = [
        {"id":1, "name":"Oliver", "age":"12", "col":"red", "dob":""},
        {"id":2, "name":"Mary May", "age":"1", "col":"blue", "dob":"14/05/1982"},
        {"id":3, "name":"Christine Lobowski", "age":"42", "col":"green", "dob":"22/05/1982"},
        {"id":4, "name":"Brendon Philips", "age":"125", "col":"orange", "dob":"01/08/1980"},
        {"id":5, "name":"Margret Marmajuke", "age":"16", "col":"yellow", "dob":"31/01/1999"},
    ]

    try:
        # with open(file.filename, 'wb') as f:
            # while contents := file.file.read(1024 * 1024):
            #     f.write(contents)
        table = pd.read_csv(file.file)
        tabledata = table.to_json(orient='records')
    except Exception:
        traceback.print_exc()
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    print(tabledata)
    return {
        "message": f"Successfully uploaded {file.filename}", 
        "table": tabledata
    }

@app.post("/chat")
def do_chat(chat_request: ChatRequest):
    print("POST /chat")

    print(chat_request.talk_input)

    response = chat(chat_request.talk_input)

    return {
        "message": response, 
    }


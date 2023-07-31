from dotenv import load_dotenv
import os
import openai
import dotenv

dotenv_file = dotenv.find_dotenv()
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def table_chat(prompt, current_df): 
    print(f"chatting using prompt: {prompt}")

    first_three_rows = current_df.head(3).to_json(orient='records')
    colstr = ""
    for col in current_df.columns:
        colstr += f' "{col}" (type: {current_df[col].dtype}),' 

    system_prompt = "Act as a code library that returns SQL code for an arbitrary natural language statement made against a data table named 'current_df', Here are the column names of the table and their data format : {colstr}. The first three rows have the following values : {first_three_rows}. Return your response in json format. The json will have three fields. The first is 'action', the second is 'sql' and the third is 'message'. The 'action' field will be a static value, either 'SQL_QUERY', 'SQL_UPDATE', or 'MESSAGE'. The 'sql' field will contain a SQL statement to run on the table to resolve the user request (or empty if the response is a message). The SQL can result in either a single value to return to the user (i.e; a count) which is a SQL_QUERY action, or a new view of the data table which is a SQL_UPDATE action. If you are unable to understand the user request or need further clarification, use the 'message' field and action to return a conversational text message in response to the user making the request. IMPORTANT: When performing an update, instead of providing an ALTER TABLE command, return a SQL SELECT statement that provides a new view of the data."

    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
    print(chat_completion)
    return chat_completion.choices[0].message.content

def error_chat(exception_summary):
   prompt = f'We recieved an exception from running the code : {exception_summary}.  Please put this error in a human readable form.'
   chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "user", "content": prompt}
        ])
   return chat_completion.choices[0].message.content

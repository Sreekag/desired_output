from fastapi import FastAPI, UploadFile, Form, Query
from fastapi.responses import FileResponse
from app.utils import save_uploaded_file, save_output_file
from app.processor.docx_processor import convert_docx_to_json, convert_docx_to_html
from app.processor.json_processor import convert_json_to_json, convert_json_to_html
from app.milvus_client import store_embedding, search_embedding, generate_embedding
import json, os
app = FastAPI()
@app.post("/convert/")
async def convert_template(
    file: UploadFile,
    title: str = Form(...),
    description: str = Form(...),
    input_type: str = Form(...),  
    output_type: str = Form(...) 
):
    file_path = save_uploaded_file(file)
    filename_no_ext = os.path.splitext(os.path.basename(file_path))[0]
    result = {}
    content = ""
    output_file = ""
    if input_type == "docx":
        if output_type == "json":
            result = convert_docx_to_json(file_path)
            content = json.dumps(result, indent=2)
            output_file = save_output_file(content, filename_no_ext, "json")
        elif output_type == "html":
            content = convert_docx_to_html(file_path)
            output_file = save_output_file(content, filename_no_ext, "html")
        else:
            return {"error": f"Unsupported output type for .docx: {output_type}"}

    elif input_type == "json":
        if output_type == "json":
            result = convert_json_to_json(file_path)
            content = json.dumps(result, indent=2)
            output_file = save_output_file(content, filename_no_ext, "json")
        elif output_type == "html":
            content = convert_json_to_html(file_path)
            output_file = save_output_file(content, filename_no_ext, "html")
        else:
            return {"error": f"Unsupported output type for .json: {output_type}"}

    else:
        return {"error": f"Unsupported input type: {input_type}"}
    embedding = generate_embedding(content)
    store_embedding(embedding, title, description, output_file)

    return {
        "title": title,
        "description": description,
        "output_path": output_file
    }
@app.get("/download/")  
def download_file(path: str):
    if os.path.exists(path):
        return FileResponse(path, filename=os.path.basename(path))
    return {"error": "File not found"}
@app.post("/search/") 
async def search_docs(query: str = Query(...)):
    query_embedding = generate_embedding(query)
    results = search_embedding(query_embedding)
    return {"matches": results}

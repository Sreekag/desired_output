import json

def convert_json_to_html(file_path: str) -> str:
    with open(file_path, "r") as f:
        data = json.load(f)
    
    html = "<html><body><h1>JSON Data</h1>"
    
    for key, value in data.items():
        html += f"<p><b>{key}:</b> {value}</p>"
    
    html += "</body></html>"
    return html

def convert_json_to_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)
def convert_json_to_html(file_path: str):
    # Read the JSON content from the file
    with open(file_path, "r") as file:
        data = json.load(file)
    
    # Start building the HTML table
    html_content = "<html><body><table border='1'>"
    
    if isinstance(data, list):  # If it's a list of items
        # Add headers
        if data:
            headers = data[0].keys()
            html_content += "<thead><tr>"
            for header in headers:
                html_content += f"<th>{header}</th>"
            html_content += "</tr></thead>"
        
        # Add rows
        html_content += "<tbody>"
        for item in data:
            html_content += "<tr>"
            for value in item.values():
                html_content += f"<td>{value}</td>"
            html_content += "</tr>"
        html_content += "</tbody>"
    else:
        html_content += "<thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>"
        for key, value in data.items():
            html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"
        html_content += "</tbody>"
    
    html_content += "</table></body></html>"
    
    return html_content
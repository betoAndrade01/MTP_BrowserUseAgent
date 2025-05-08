#!/usr/bin/env python3

import json
import base64
from pathlib import Path
from fastapi import FastAPI, Request
import prettyprinter
import uvicorn

prettyprinter.install_extras()

# Inicializar la aplicación FastAPI
app = FastAPI()

# Función utilitaria para guardar capturas en base64 como PNG
def b64_to_png(b64_string: str, output_file):
    with open(output_file, "wb") as f:
        f.write(base64.b64decode(b64_string))

# Endpoint para recibir y guardar los datos del agente
@app.post("/post_agent_history_step")
async def post_agent_history_step(request: Request):
    data = await request.json()
    prettyprinter.cpprint(data)

    recordings_folder = Path("src/tests/recordings")
    recordings_folder.mkdir(parents=True, exist_ok=True)

    screenshot_folder = Path("src/tests/capturas")
    screenshot_folder.mkdir(parents=True, exist_ok=True)

    existing_numbers = [
        int(p.stem) for p in recordings_folder.glob("*.json") if p.stem.isdigit()
    ]
    next_number = max(existing_numbers, default=0) + 1

    file_path = recordings_folder / f"{next_number}.json"
    with file_path.open("w") as f:
        json.dump(data, f, indent=2)

    screenshot_path = "no screenshot"
    if "website_screenshot" in data and data["website_screenshot"]:
        screenshot_path = screenshot_folder / f"{next_number}.png"
        b64_to_png(data["website_screenshot"], screenshot_path)

    return {"status": "ok", "message": f"Saved to {file_path} and {screenshot_path}"}

# Código para correr el servidor
if __name__ == "__main__":
    print("Starting API on http://0.0.0.0:9000")
    uvicorn.run("api:app", host="0.0.0.0", port=9000, reload=True)

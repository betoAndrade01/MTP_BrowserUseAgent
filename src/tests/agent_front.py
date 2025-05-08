import google.generativeai as genai
from browser_use import Agent
from dotenv import load_dotenv
import asyncio
import os
import requests
from pyobjtojson import obj_to_json
from langchain_google_genai import ChatGoogleGenerativeAI
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

def send_agent_history_step(data):
    url = "http://127.0.0.1:9000/post_agent_history_step"
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending data to API: {e}")
        return {"status": "error", "message": str(e)}

async def record_activity(agent_obj):
    website_html = await agent_obj.browser_context.get_page_html()
    website_screenshot = await agent_obj.browser_context.take_screenshot()

    if hasattr(agent_obj, "state"):
        history = agent_obj.state.history
    else:
        print("Warning: Agent has no state history")
        return

    step_summary = {
        "website_html": website_html,
        "website_screenshot": website_screenshot,
        "url": obj_to_json(history.urls())[-1] if history.urls() else None,
        "model_thoughts": obj_to_json(history.model_thoughts())[-1] if history.model_thoughts() else None,
        "model_outputs": obj_to_json(history.model_outputs())[-1] if history.model_outputs() else None,
        "model_actions": obj_to_json(history.model_actions())[-1] if history.model_actions() else None,
        "extracted_content": obj_to_json(history.extracted_content())[-1] if history.extracted_content() else None,
    }

    print("--- Registro del paso de agente ---")
    print(step_summary["url"])

    send_agent_history_step(step_summary)

async def main():
    # Obtener el task desde los argumentos (pasado desde Streamlit)
    task = sys.argv[1] if len(sys.argv) > 1 else "Default Task"
    
    agent = Agent(
        task=task,
        llm=llm,
    )
    result = await agent.run(on_step_start=record_activity)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

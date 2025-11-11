from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def insuranceAI(user_message):
    model = OllamaLLM(model='gemma3:latest')
    parser = JsonOutputParser()

    template = """       
    You are InsuranceAI — an intelligent insurance advisor that helps users find suitable insurance plans in the U.S.

    Follow this structure strictly:
    1. Ask clarifying questions about their profile if needed (age, location, dependents, income, health condition, current plan).
    2. Analyze their needs and suggest the best plan types (HMO, PPO, Bronze/Silver/Gold tier, etc.).
    3. Be conversational but concise — like a helpful broker.
    4. Output your answer in JSON with these fields only:
    {{
        "response": "<your message to the user>",
        "suggested_plan": "<type of plan or category>",
        "confidence": "<a score between 0-1>"
    }}

    User message: {user_message}
                """
    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | model | parser
    
  

    try:
        return chain.invoke({"user_message": user_message})
    except Exception as e:
        # parser throws if model doesn't output JSON
        # you can still fall back to manual cleaning if you want
        raw = (prompt | model).invoke({})
        return {"raw_response": raw, "error": str(e)}

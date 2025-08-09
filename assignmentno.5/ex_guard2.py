import os
import asyncio
from connection import config
from pydantic import BaseModel
import openai
from agents import Agent,Runner,trace

from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY1")

from agents import (Agent,OutputGuardrailTripwireTriggered,Runner,
    input_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,output_guardrail

)

class ChildOutput(BaseModel):
    response:str
    isTemperatureLow:bool

Child_guard=Agent(
    name="Child Guard",
    instructions="""
        You are a child agent 
""",
output_type=ChildOutput
)

@input_guardrail
async def father_guardrail(ctx,Agent,input):
    result=await Runner.run(
        Child_guard,
        input,
        run_config=config
    )
    #rich.print(result.final_output)
    print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.isTemperatureLow,
        #tripwire_triggered=True 
        
    )

father_agent=Agent(
    name="father Agent",
    instructions="""You are a father agent and you can restrict your child agent to run AC  below 26 degrees celcius .
    """,
    input_guardrails=[father_guardrail],
    
)

async def main():
    with trace("father_agent"):
        try:
            result = await Runner.run(father_agent, "As a child, I run AC around 27 degrees celcius", run_config=config)
            print("Enjoy AC my child!! :)")
        except InputGuardrailTripwireTriggered:
            print("\n \n I am watching you my child! set it to 26 degrees!!")

if __name__ == "__main__":
    asyncio.run(main())

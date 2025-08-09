import os
#import rich
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

class StudentOutput(BaseModel):
    response:str
    #isSeatAvailable:bool

student_guard=Agent(
    name="student Guard",
    instructions="""
        You are a student agent for admin department
""",
output_type=StudentOutput,
)

@input_guardrail
async def admin_guardrail(ctx,Agent,input):
    result=await Runner.run(
        student_guard,
        input,
        run_config=config
    )
    #rich.print(result.final_output)
    print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        #tripwire_triggered=result.final_output.isSeatAvailable,
        tripwire_triggered=True 
        
    )

admin_agent=Agent(
    name="Admin Agent",
    instructions="""You are an academic admin agent and you have the authority to cancel request.
dont allow slot change
    """,
    input_guardrails=[admin_guardrail],
    
)

async def main():
    with trace("admin_agent"):
        try:
            result = await Runner.run(admin_agent, ": I want to change my class timings 😭😭", run_config=config)
            print("Your timings could be changed")
        except InputGuardrailTripwireTriggered:
            print("\n As for now,We can't do it for you now. Sorry.Try to change in next quarter")

if __name__ == "__main__":
    asyncio.run(main())

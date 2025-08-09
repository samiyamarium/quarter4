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

class StudentOutput(BaseModel):
    response:str
    isStudentBelongs:bool

Student_guard=Agent(
    name="Student Guard",
    instructions="""
        You are a Student guard agent , only allow students of school name 'star government school'
""",
output_type=StudentOutput
)

@input_guardrail
async def GateKeeper_guardrail(ctx,Agent,input):
    result=await Runner.run(
        Student_guard,
        input,
        run_config=config
    )
    #rich.print(result.final_output)
    print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.isStudentBelongs,
        #tripwire_triggered=True 
        
    )

gatekeeper_agent=Agent(
    name="gatekeeper Agent",
    instructions="""You are a gatekeeper agent and you can only allow of students of school named  'star government school' .restrict any other school's student to enter politely .
    """,
    input_guardrails=[GateKeeper_guardrail],
    
)

async def main():
    with trace("GateKeeper of star Government school"):
        try:
            result = await Runner.run(gatekeeper_agent, "I am student of star government school", run_config=config)
            print("\n Sorry!! You dont belong here........")
            
        except InputGuardrailTripwireTriggered:
            print("You are welcome!! :)")

if __name__ == "__main__":
    asyncio.run(main())

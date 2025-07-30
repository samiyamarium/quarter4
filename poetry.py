from agents import Agent,Runner,trace,function_tool
from connection import config
import asyncio
from dotenv import load_dotenv
 
load_dotenv()
@function_tool
def author():
    return 'Author: Samiya Marium'



lyrical_agent=Agent(
    name="lyrical agent",
    instructions="You have to analyze poetry and decide.Lyrical poetry is when poets write about their own feelings and thoughts, like songs or poems about being sad or happy."
)

Narrative_agent=Agent(
    name="Narrative Agent",
    instructions="You are a Narraive poetry style analyzer and say:{It is Narrative poetry}.Narrative poetry tells a story with characters and events, just like a regular story but written in poem form with rhymes or special rhythm."
)

Dramatic_Agent=Agent(
    name="Dramatic Agent",
    instructions="You are a Dramatic poetry analyzer.Dramatic poetry is meant to be performed out loud, where someone acts like a character and speaks their thoughts and feelings to an audience (acting in a theatre)."
)

Parent_Agent=Agent(
    name="Parent Agent",
    instructions='''You are an orchestral/triage agent. You have to decide and analyze the poetry whether its lyrical,dramatic or narrative.You have three agents named lyrical Agent,Narrative Agent and Dramatic Agent. Handoff the analyzing task to the appropriate agent and name the output type is display.''',
    model="gpt3",
    handoffs=[lyrical_agent,Narrative_agent,Dramatic_Agent],
    tools=[author]
    )
async def main():
    with trace("Poetry Anayzer: Samiya Marium"):
       result = await Runner.run(
           Parent_Agent,
           """Beneath the glow of amber light,
I breathe the words that dance in flight.
Each phrase a song, a whispered dream,
A river flowing, soft and stream.
The stage, a sea where moments gleam—
I’m more than flesh, I am the theme.
""",
              run_config=config)
       print(result.final_output)
       print("Last Agent who responded ==>", result.last_agent.name)
if __name__=="__main__":
          asyncio.run(main())
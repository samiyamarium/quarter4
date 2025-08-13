import os
import openai
import asyncio
from connection import config
from agents import Agent, RunContextWrapper,Runner,function_tool,trace
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY1")

'''class UserInfo(BaseModel):
    user_id:int | str
    name:str
user=UserInfo(user_id=0, name="Samiya") , UserInfo(user_id="sd", name="Marium"), UserInfo(user_id=2, name="Mary")'''

class BankAccount(BaseModel):
    account_number:int|str|float
    customer_name:str
    account_balance:int|float
    account_type:str|int


bank_account = BankAccount(
    account_number="ACC-789456",
    customer_name="Fatima Khan",
    account_balance=75500.50,
    account_type="savings"
)

class StudentProfile(BaseModel):
    student_id:str|int
    student_name:str
    current_semester:int|float
    total_courses:int

student = StudentProfile(
    student_id="STU-456",
    student_name="Hassan Ahmed",
    current_semester=4,
    total_courses=5
)

@function_tool
def get_student_info(wrapper:RunContextWrapper[StudentProfile]):
    return f'The Student info is as follows: {wrapper.context.student_name} bearing ID {wrapper.context.student_id} enrolled in semester  {wrapper.context.current_semester} with a total of {wrapper.context.total_courses} courses .. '
Student_agent=Agent(
    name="Student Agent",
    instructions="You are a helpful student agent.call the tool.Provide info of students ",
    tools=[get_student_info]
)
class LibraryBook(BaseModel):
    book_id:str|int
    book_title:str|int
    author_name:str
    is_available:bool

library_book = LibraryBook(
    book_id="BOOK-123",
    book_title="Python Programming",
    author_name="John Smith",
    is_available=True
)

@function_tool
def get_book_info(wrapper:RunContextWrapper[LibraryBook]):
    return f'The book titled {wrapper.context.book_title} written by {wrapper.context.author_name} bearing ID {wrapper.context.book_id}.BOOK_STATUS : {wrapper.context.is_available}'
Library_agent=Agent(
            name="Library Agent",
            instructions='You are a helpful Library agent. Call the tool and provide info accordingly',
            tools=[get_book_info]    
)

'''@function_tool
def get_user_info(wrapper:RunContextWrapper[UserInfo]):
    return f'The User info is {wrapper.context}'
personal_agent=Agent(
    name="Agent",
    instructions="You are a helpful assistant,always call the tool, call the context from high to low user id. give priority to integer user id in list.indent with numbers as list items",
    tools=[get_user_info]
)'''

@function_tool
def get_bank_info(wrapper:RunContextWrapper[BankAccount]):
    return f"The customer named {wrapper.context.customer_name} bearing Account number {wrapper.context.account_number} has a total of {wrapper.context.account_balance} with account type : {wrapper.context.account_type}"
Bank_agent=Agent(
    name="Bank Agent",
    instructions="You are a helpful banking assistant , use tool and tell Bank accont info as asked and provided in local context.",
    tools=[get_bank_info]
)
async def main():
    with trace("LLM given context in Local (For Bank Account)"):
       result=await Runner.run( 
           Bank_agent,
        'Tell customer name with account type and acccount balance with acccount number from context ',
           run_config=config,
           context=bank_account     
         )
    print("BANK AGENT : ",result.final_output)
async def main1():
    with trace('LLM with Local (for student agent)'):
        result=await Runner.run(
            Student_agent,
            'Tell Student name with student id and current semester enrolment with number of courses',
            run_config=config,
            context=student
        )
    print("STUDENT AGENT : " ,result.final_output)

async def main2():
    with trace('LLM and Local context(with Library book info)'):
        result=await Runner.run(
            Library_agent,
            'You are a helpful Library agent. provide info accordingly using context',
            run_config=config,
            context=library_book
        )
    print("LIBRARY AGENT : ",result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main1())
    asyncio.run(main2())

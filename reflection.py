from langchain_core.messages import AIMessage, HumanMessage
from typing import List
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable

def create_reflection_agent(llm: BaseChatModel, prompt: str, num_reflections: int) -> Runnable:
    class ReflectionAgent(Runnable):
        def __init__(self, llm: BaseChatModel, prompt: str, num_reflections: int):
            self.llm = llm
            self.prompt = SystemMessage(content=prompt)
            self.num_reflections = num_reflections
            self.reflection = """You are an AI agent to that reviews the output of another AI Agent. You will be given the tasks that the other AI agent was given to do, and the output of the other AI agent. 
Review the output and any revisions of the other AI Agent, and provide critiques and recommendations based on the task it was supposed to do. Always ensure the the AI Agent replied with a final draft, no other response.
If the AI Agent output needs no further revisions, then end your reply with 'END: Produce the final output'"""

            # reflect_prompt = [
            #         self.reflect,
            #         HumanMessage(content="Summarize your tasks")
            #     ]            
            # reflection_response = self.llm.invoke(reflect_prompt)  

        def invoke(self, query: str) -> str:
            generate_history = [self.prompt, HumanMessage(content=query)]

            initial = [self.prompt, HumanMessage(content="Quickly summarize your tasks")]
            initial_response = self.llm.invoke(initial)
            print(initial_response)

            reflect_history = [SystemMessage(content=self.reflection + "This is the AI Agent's tasks:\n" + initial_response.content + "\nThis is the task the AI Agent was doing:\n" + query)]

            output_response = self.llm.invoke(generate_history)
            output = output_response.content

            generate_history.append(AIMessage(content=output))
            reflect_history.append(HumanMessage(content=output))    

            for _ in range(self.num_reflections):

                reflection_response = self.llm.invoke(reflect_history)
                reflection = reflection_response.content
                if reflection.endswith("END: Produce the final output"):
                    self.num_reflections = 0                  

                reflect_history.append(AIMessage(content=reflection))
                generate_history.append(HumanMessage(content=reflection))

                output_response = self.llm.invoke(generate_history)
                output = output_response.content

                generate_history.append(AIMessage(content=output))
                reflect_history.append(HumanMessage(content=output))

                print("\nReview:")
                print(reflection)

            return output

        async def arun(self, query: str) -> str:
            return self.run(query)

    return ReflectionAgent(llm, prompt, num_reflections)

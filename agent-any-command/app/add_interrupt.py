from typing import Callable
from langchain_core.tools import BaseTool, tool as create_tool
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt
from langgraph.prebuilt.interrupt import HumanInterruptConfig, HumanInterrupt
from langgraph.types import Command


def human_in_the_loop_prompt(interrupt):
    data = interrupt[0]
    description = data.value[0]["description"]
    action = data.value[0]["action_request"]["action"]
    command_string = data.value[0]["action_request"]["args"]["command_string"]

    print("action: " + action)
    print(command_string)
    user_input = input(description + " OK?[y/N]>>> ").strip()

    if user_input in ('y', 'Y', 'yes', 'YES', 'Yes', 'はい'):
        return Command(resume=[{"type": "accept"}])

    user_input = input("If you have feedback, please write.>>> ").strip()
    if user_input != '':
        message = "Command is rejected by human. Feedback: " + user_input
        return Command(resume=[{"type": "response", "args": message}])

    return Command(resume=[{"type": "deny"}])


def add_human_in_the_loop(
    tool: Callable | BaseTool,
    *,
    interrupt_config: HumanInterruptConfig = None,
) -> BaseTool:
    """Wrap a tool to support human-in-the-loop review."""
    if not isinstance(tool, BaseTool):
        tool = create_tool(tool)

    if interrupt_config is None:
        interrupt_config = {
            "allow_accept": True,
            "allow_edit": True,
            "allow_respond": True,
        }

    @create_tool(  
        tool.name,
        description=tool.description,
        args_schema=tool.args_schema
    )
    async def call_tool_with_interrupt(config: RunnableConfig, **tool_input):
        request: HumanInterrupt = {
            "action_request": {
                "action": tool.name,
                "args": tool_input
            },
            "config": interrupt_config,
            "description": "Please review the tool call."
        }
        response = interrupt([request])[0]  
        # approve the tool call
        if response["type"] == "accept":
            tool_response = await tool.ainvoke(tool_input, config)
        # update tool call args
        elif response["type"] == "edit":
            tool_input = response["args"]["args"]
            tool_response = await tool.ainvoke(tool_input, config)
        # respond to the LLM with user feedback
        elif response["type"] == "response":
            user_feedback = response["args"]
            tool_response = user_feedback
        elif response["type"] == "deny":
            raise ValueError("Your command is rejected by human. Ask how you should do to human")
        else:
            raise ValueError(f"Unsupported interrupt response type: {response['type']}")

        return tool_response

    return call_tool_with_interrupt

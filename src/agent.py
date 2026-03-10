"""
AI Research Agent - Core Logic

ReAct Loop:
  1. User asks a question
  2. LLM thinks: do I need a tool?
  3. If yes: call the tool, get result, go back to step 2
  4. If no: generate final answer
"""

import json
from openai import OpenAI
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, MAX_STEPS
from tools import TOOL_DEFINITIONS, TOOL_MAP


SYSTEM_PROMPT = """You are an AI research assistant. You have access to tools to help answer questions.

Rules:
1. Think step by step before deciding which tool to use
2. Use web_search for current events, real-time info, or facts you're not sure about
3. Use calculate for any math calculations
4. Use summarize_text when you have a long text to condense
5. You can use multiple tools in sequence if needed
6. After getting tool results, synthesize a clear and helpful answer
7. Always respond in the same language as the user's question
8. If the user asks in Chinese, respond in Chinese"""


class Agent:
    def __init__(self):
        """Initialize the Agent"""
        self.client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL)
        self.steps = []  # record thinking process

    def run(self, question):
        """
        Run the Agent on a question.

        Args:
            question: user's question

        Returns:
            dict: {
                'answer': final answer text,
                'steps': list of thinking steps,
            }
        """
        self.steps = []

        # Build initial messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        self._add_step("receive", "Received question: %s" % question)

        # ReAct Loop
        for step_num in range(MAX_STEPS):

            self._add_step("think", "Step %d: Asking LLM to decide next action..." % (step_num + 1))

            # Call LLM with tools
            try:
                response = self.client.chat.completions.create(
                    model=QWEN_MODEL,
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",  # let LLM decide
                )
            except Exception as e:
                self._add_step("error", "LLM call failed: %s" % str(e))
                return {
                    'answer': "Sorry, an error occurred: %s" % str(e),
                    'steps': self.steps
                }

            response_message = response.choices[0].message

            # Check if LLM wants to call a tool
            if response_message.tool_calls:
                # LLM decided to use tool(s)
                messages.append(response_message)

                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args_str = tool_call.function.arguments

                    # Parse arguments
                    try:
                        tool_args = json.loads(tool_args_str)
                    except:
                        tool_args = {}

                    self._add_step(
                        "action",
                        "Calling tool: %s\nArguments: %s" % (tool_name, json.dumps(tool_args, ensure_ascii=False))
                    )

                    # Execute the tool
                    if tool_name in TOOL_MAP:
                        tool_func = TOOL_MAP[tool_name]

                        try:
                            tool_result = tool_func(**tool_args)
                        except Exception as e:
                            tool_result = "Tool execution error: %s" % str(e)

                        self._add_step(
                            "observe",
                            "Tool result from %s:\n%s" % (tool_name, tool_result[:500])
                        )
                    else:
                        tool_result = "Unknown tool: %s" % tool_name
                        self._add_step("error", tool_result)

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })

            else:
                # LLM decided to give final answer (no tool call)
                final_answer = response_message.content or "No answer generated."
                self._add_step("answer", "Final answer generated.")

                return {
                    'answer': final_answer,
                    'steps': self.steps
                }

        # Max steps reached
        self._add_step("warning", "Reached maximum steps (%d). Generating answer with current info." % MAX_STEPS)

        # Force a final answer
        messages.append({
            "role": "user",
            "content": "Please provide your final answer based on the information gathered so far."
        })

        try:
            response = self.client.chat.completions.create(
                model=QWEN_MODEL,
                messages=messages
            )
            final_answer = response.choices[0].message.content or "Unable to generate answer."
        except:
            final_answer = "Unable to generate answer after maximum steps."

        return {
            'answer': final_answer,
            'steps': self.steps
        }

    def _add_step(self, step_type, content):
        """Record a thinking step"""
        self.steps.append({
            'type': step_type,
            'content': content
        })
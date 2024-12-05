import time
import typing as t

from openai import OpenAI

from ai.prompts import *


def sources_to_class_string(sources: list[t.Any]) -> str:
    class_strings = []
    for source in sources:
        source_class = source._source_class
        cols = []
        for attr in dir(source_class):
            if attr.startswith("_") or attr.startswith("__"):
                continue
            field = getattr(source_class, attr)
            type = repr(field.type)
            description = (
                field.description.strip().replace("\n", "") if field.description else ""
            )
            column = (
                f'{attr}: {repr(field.type)} = Field(description="""{description}""")'
            )
            cols.append("  " + column)

        class_string = f"class {source_class.__name__}:\n"
        class_string += "\n".join(cols)
        class_strings.append(class_string)

    return "\n".join(class_strings)


def make_prompt(question, sources):
    classes = sources_to_class_string(sources)

    return f"""
Here are examples:
prompt: {prompt_1}
answer: {answer_1}
-------
prompt: {prompt_4}
answer: {answer_4}
-------
prompt: {prompt_5}
answer: {answer_5}

We want a python query model for:
prompt: {question}
{classes}
"""


def instruct(prompt: str, sources):
    client = OpenAI()
    assistant = client.beta.assistants.create(
        name="Midi",
        instructions=SYSTEM_MESSAGE,
        model="gpt-4-turbo-preview",
    )
    thread = client.beta.threads.create()
    prompt = make_prompt(prompt, sources)
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Just return the model and nothing else. You are an expert at writing python and using the custom data transform library.",
    )

    while run.status in ["queued", "in_progress", "cancelling"]:
        time.sleep(1)  # Wait for 1 second
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        resp = messages.data[0].content[0].text.value
        return resp
    else:
        raise Exception("Run failed")

import time

from langfuse import Langfuse
from litellm import completion as litellm_completion

langfuse = Langfuse(host="https://us.cloud.langfuse.com")


def completion(*args, **kwargs):
    stream = kwargs.get("stream", False)
    start_time = time.time()

    user_id = kwargs.pop("user_id")
    tags = kwargs.pop("tags", [])
    trace = langfuse.trace(user_id=user_id, input=kwargs.get("messages"), tags=tags)

    langfuse_payload = {
        "start_time": start_time,
        "model": kwargs.get("model"),
        "input": kwargs.get("messages"),
    }

    if stream:
        result_generator = litellm_completion(*args, **kwargs)
        collected_output = ""

        def streaming_generator():
            nonlocal collected_output
            for result in result_generator:
                chunk = result.choices[0].delta.content
                if chunk is not None:
                    collected_output += chunk
                yield result

            end_time = time.time()
            langfuse_payload.update(
                {
                    "end_time": end_time,
                    "output": collected_output,
                }
            )
            trace.generation(**langfuse_payload)
            trace.update(end_time=end_time, output=collected_output)

        return streaming_generator()
    else:
        result = litellm_completion(*args, **kwargs)
        output = result.choices[0].message.content
        end_time = time.time()

        langfuse_payload.update(
            {
                "end_time": end_time,
                "output": output,
            }
        )
        trace.generation(**langfuse_payload)
        trace.update(end_time=end_time, output=output)

        return result

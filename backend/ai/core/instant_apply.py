import os
from typing import Iterator, List, Optional

from ai.core.custom_litellm import completion
from ai.core.models import InstantApplyRequestBody


def stream_instant_apply(
    *, payload: InstantApplyRequestBody, user_id: Optional[str] = None, tags: Optional[List[str]] = None
) -> Iterator[str]:
    response = completion(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0,
        model="claude-3-5-sonnet-20240620",
        messages=[
            {
                "role": "system",
                "content": 'You are a smart applier. You are similar to Cursor\'s "Smart Apply" functionality, in that you take two pieces of code and merge them together. Rewrite the entire file. Only output the rewritten file. Do NOT change anything else other than the "change" section. Do NOT add aditional text like "Here is the updated file:" or anything like that. Just output the rewritten file. And do NOT enclose the file in ```sql or ``` or anything like that. Just output the rewritten file. Finally, do NOT modify the formatting of the file. Keep the same formatting even if it is not correct.',
            },
            {
                "role": "user",
                "content": f"Base file:\n```{payload.base_file}```\n\nChange:\n```{payload.change}```",
            },
        ],
        stream=True,
        user_id=user_id,
        tags=["instant_apply", *(tags or [])],
    )

    for chunk in response:
        yield chunk.choices[0].delta.content or ""

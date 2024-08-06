from ai.ai import instruct


class GenAIService:
    def __init__(self, sources):
        self.sources = sources

    def prompt(self, prompt: str):
        sources = []
        for source in self.sources:
            source_class = source._source_class
            if (
                ".satscores" in source_class._unique_name.lower()
                or ".schools" in source_class._unique_name.lower()
            ):
                sources.append(source)

        response = instruct(
            prompt=prompt,
            sources=sources,
        )
        return response

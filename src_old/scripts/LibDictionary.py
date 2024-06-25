from dataclasses import dataclass

@dataclass
class DictionaryEntry:
    string_id: str
    entry: str
    short_meaning: str
    meaning: str
    examples: str
    comments: str

    def __str__(self):
        return f"""
{self.entry} ({self.string_id}):
    {self.short_meaning}
    {self.meaning}
    {self.examples}
    {self.comments}"""

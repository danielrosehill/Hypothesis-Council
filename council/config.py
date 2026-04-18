from dataclasses import dataclass


@dataclass(frozen=True)
class Member:
    name: str
    model: str
    lineage: str


COUNCIL: list[Member] = [
    Member("Claude Sonnet 4.5", "anthropic/claude-sonnet-4.5", "Anthropic"),
    Member("Grok 4", "x-ai/grok-4", "xAI"),
    Member("MiniMax M2", "minimax/minimax-m2", "MiniMax"),
]

SYNTHESISER = Member("Claude Sonnet 4.5 (synth)", "anthropic/claude-sonnet-4.5", "Anthropic")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

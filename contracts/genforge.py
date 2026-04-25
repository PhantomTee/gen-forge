from genlayer import *

class GenForge:
    def __init__(self):
        # Stores the prompt and the resulting code
        self.drafts = {} 

    @gl.public.write
    def draft_contract(self, user_prompt: str):
        """
        Consensus-driven LLM call to generate a new contract.
        """
        system_instructions = (
            "You are a GenLayer Python Expert. Generate ONLY a valid "
            "Python class using the GenLayer SDK. No prose, no backticks."
        )

        # This is where the magic happens
        generated_code = gl.llm.generate(
            prompt=f"Write a GenLayer contract for: {user_prompt}",
            system_prompt=system_instructions,
            model="large" # Uses the high-power model
        )

        self.drafts[user_prompt] = generated_code
        return f"Architected: {user_prompt}"

    @gl.public.view
    def get_code(self, user_prompt: str) -> str:
        return self.drafts.get(user_prompt, "No draft found.")

# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import typing
import json
import hashlib

# Constants
MAX_PROMPT_LENGTH = 1000
MAX_CODE_LENGTH = 50000  

class GenForge(gl.Contract):
    """GenForge: On-chain Intelligent Contract Architect using LLM consensus"""

    owner: Address
    drafts: TreeMap[str, str]          
    code_hashes: TreeMap[str, str]     

    def __init__(self):
        self.owner = gl.message.sender_address
        # GenVM automatically initializes TreeMaps; do not assign them here.

    def _normalize_prompt(self, prompt: str) -> str:
        """Normalize prompt for use as key - trim whitespace and lowercase"""
        return prompt.strip().lower()

    def _hash_prompt(self, prompt: str) -> str:
        """Create a deterministic hash for the prompt using standard hashlib"""
        normalized = self._normalize_prompt(prompt)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    @gl.public.write
    def draft_contract(self, user_prompt: str) -> str:
        """Generate a new Intelligent Contract using LLM + validator consensus."""
        if not user_prompt or len(user_prompt.strip()) < 10:
            raise gl.vm.UserError("Error: Prompt too short. Provide a detailed description.")
        
        if len(user_prompt) > MAX_PROMPT_LENGTH:
            raise gl.vm.UserError(f"Error: Prompt too long. Maximum {MAX_PROMPT_LENGTH} characters.")

        prompt_hash = self._hash_prompt(user_prompt)

        def leader_fn():
            prompt = f"""You are a senior GenLayer Python expert.
Create a useful GenLayer Intelligent Contract for this request: {user_prompt}

CRITICAL GENLAYER RULES:
1. The VERY FIRST LINE must exactly be: # {{ "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }}
2. NEVER use 'int', 'list', or 'dict' for storage variables. Use 'u256', 'u32', 'i64', 'DynArray', or 'TreeMap'.
3. To get the caller address, use 'gl.message.sender_address'.
4. For errors, use 'raise gl.vm.UserError("message")'.
5. Do not initialize storage collections in __init__.
6. Classes MUST inherit from gl.Contract.
7. Methods MUST use @gl.public.write or @gl.public.view.

Respond ONLY with this JSON format:
{{"code": "exact python code as a string"}}"""
            
            return gl.nondet.exec_prompt(prompt, response_format="json")

        def validator_fn(leaders_res) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            leader_code = leaders_res.calldata.get("code", "")
            if not leader_code or "class" not in leader_code or "gl.Contract" not in leader_code:
                return False

            val_prompt = f"""Review this GenLayer Contract code:
{leader_code}
Does it fulfill this request: "{user_prompt}" and follow GenLayer rules?
Respond ONLY in JSON: {{"is_valid": true}} or {{"is_valid": false}}"""
            
            val_res = gl.nondet.exec_prompt(val_prompt, response_format="json")
            return val_res.get("is_valid", False)

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        generated_code = result.get("code", "")

        if not generated_code or len(generated_code.strip()) == 0:
            raise gl.vm.UserError("Error: LLM generation failed. Please try again.")

        if len(generated_code) > MAX_CODE_LENGTH:
            raise gl.vm.UserError(f"Error: Generated code too large. Max {MAX_CODE_LENGTH}.")

        cleaned = generated_code.strip()
        if "```python" in cleaned:
            cleaned = cleaned.split("```python")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].strip()

        magic_header = '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }'
        if magic_header not in cleaned:
            cleaned = f"{magic_header}\nfrom genlayer import *\n\n{cleaned}"

        self.drafts[prompt_hash] = cleaned
        self.code_hashes[prompt_hash] = user_prompt 

        return f"✅ Successfully architected: {user_prompt[:120]}..."

    @gl.public.view
    def get_code(self, user_prompt: str) -> str:
        prompt_hash = self._hash_prompt(user_prompt)
        code = self.drafts.get(prompt_hash)
        return code if code is not None else "No draft found for this prompt."

    @gl.public.view
    def get_all_prompts(self) -> list[str]:
        prompts = []
        for p in self.code_hashes.values():
            prompts.append(p)
        return prompts

    @gl.public.view
    def get_draft_count(self) -> u32:
        count = 0
        for _ in self.drafts.keys():
            count += 1
        return u32(count)

    @gl.public.write
    def clear_drafts(self) -> str:
        if gl.message.sender_address != self.owner:
            raise gl.vm.UserError("Unauthorized: Only the owner can clear drafts.")
        
        # Iterate to delete, as assigning TreeMap() is illegal
        draft_keys = []
        for k, _ in self.drafts.items():
            draft_keys.append(k)
        for k in draft_keys:
            del self.drafts[k]

        hash_keys = []
        for k, _ in self.code_hashes.items():
            hash_keys.append(k)
        for k in hash_keys:
            del self.code_hashes[k]

        return "All drafts cleared."
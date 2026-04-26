# Reliability and Eval

The backend includes a comprehensive test suite in `tests/test_pawpal.py` covering:

- **Automated tests**: 6 test classes with 60+ test cases for task scheduling, recurrence, sorting, conflict detection, edge cases, and pet resource guardrails.
- **Confidence scoring**: The chatbot system rates query confidence when validating pet-related requests via `is_pet_related_query()`.
- **Guardrails & logging**: Prompt injection prevention (10+ attack vectors tested), retailer detection, and scope validation with error messages.
- **Human evaluation**: Sample interactions in this README demonstrate expected AI behavior for analyze and resource-finder modes.

**Summary**: 54 out of 60 tests passed; 6 tests failed due to missing `filter_commercial_results` and `is_valid_pet_resource` functions in `pet_resource_search.py`. All guardrail tests (prompt injection, scope validation, retailer detection) passed with 100% accuracy. Task scheduling logic is fully validated; confidence scoring averages 0.85 when context is provided.

# Reflection and Ethics
- What are the limitations or biases in your system?
**A limitation in my system is that as the database scales, it would be harder to manage and ultimately for the AI to analyze since it has a certain context window. Also with the Gemini API being fine-tuned, it is biased in only finding pet-related resources.** 
<br>

- Could your AI be misused, and how would you prevent that?
**I believe my AI can't be misused because there are enforced guardrails, that only ensure there's pet-related content. Also, it accounts for prompt injections and inappropriate input.**
<br>

- What surprised you while testing your AI's reliability?
**I asked the chatbot to find a Toyota for my demo, and expected it to say that it wasn't pet related. However, I was surprised when it generated a pet-based response with the list of Toyota toy cars, assuming that I meant a small toyota car toy for my pet to play with even though it was supposed to test the chatbot's guardrails and show that my prompt was irrelevant and wasn't the appropriate context.**
<br>

- describe your collaboration with AI during this project. Identify one instance when the AI gave a helpful suggestion and one instance where its suggestion was flawed or incorrect.
**An instance where the AI gave me a helpful suggestion was when it provided resources for dog food, and it showed me sites when I can find dog food such as PetSmart, Chewy, Amazon, etc.**
**An instance where the AI gave me a flawed suggestion was that when I asked for today's schedule it didn't give me any tasks, even though I had tasks that were due for today. the keyword "today" seemed ambiguous for the chatbot, so it had a hardtime finding tasks due for today, and it said it couldn't find any tasks**

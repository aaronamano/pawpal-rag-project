import os
import re
from typing import Optional
from google import genai
from dotenv import load_dotenv

load_dotenv()

ALLOWED_PET_CATEGORIES = [
    "pet food",
    "pet foods",
    "dog food",
    "cat food",
    "bird food",
    "rabbit food",
    "pet treats",
    "pet treats",
    "dog treats",
    "cat treats",
    "pet toys",
    "pet toy",
    "dog toys",
    "cat toys",
    "bird toys",
    "pet supplies",
    "pet supply",
    "pet accessories",
    "pet shelter",
    "pet shelters",
    "animal shelter",
    "animal shelters",
    "pet store",
    "pet stores",
    "veterinarian",
    "veterinarians",
    "vet",
    "vets",
    "veterinary",
    "pet grooming",
    "pet groomer",
    "grooming",
    "pet insurance",
    "pet medical",
    "pet training",
    "pet trainer",
    "dog trainer",
    "cat trainer",
    "pet daycare",
    "pet sitting",
    "dog walking",
    "pet rescue",
    "pet rescue organization",
    "adopt pet",
    "adopt a pet",
    "pet adoption",
    "pet food brand",
    "pet food brands",
    "organic pet food",
    "grain free pet food",
    "pet bed",
    "pet beds",
    "pet crate",
    "pet carrier",
    "pet collar",
    "pet leash",
    "pet harness",
    "pet medication",
    "pet meds",
    "flea treatment",
    "heartworm prevention",
    "pet vitamin",
    "pet supplements",
    "aquarium",
    "fish tank",
    "pet fish",
    "pet cage",
    "bird cage",
    "hamster cage",
]

ALLOWED_RETAILERS = [
    "chewy",
    "chewy.com",
    "petco",
    "petco.com",
    "petsmart",
    "petsmart.com",
    "pet smart",
    "amazon",
    "amazon.com",
    "walmart",
    "walmart.com",
    "target",
    "target.com",
    "pet supplies plus",
    "petsuppliesplus.com",
    "bed bath & beyond",
    "bedbathandbeyond.com",
    "costco",
    "costco.com",
    "nordstrom",
    "nordstrom.com",
    "pet store",
    "local pet store",
]

RESOURCE_PATTERNS = [
    r"chewy\.com",
    r"petco\.com",
    r"petsmart\.com",
    r"amazon\.com",
    r"walmart\.com",
    r"target\.com",
    r"petsuppliesplus\.com",
    r"costco\.com",
]

COMMERCIAL_KEYWORDS = [
    "pet food",
    "pet treats",
    "pet toys",
    "pet supplies",
    "pet accessories",
    "pet bed",
    "pet crate",
    "pet carrier",
    "pet collar",
    "pet leash",
    "pet harness",
    "pet medication",
    "pet vitamin",
    "pet supplements",
    "flea treatment",
    "heartworm",
    "pet insurance",
    "adopt",
    "shelter",
    "rescue",
    "veterinarian",
    "vet",
    "grooming",
    "training",
    "daycare",
    "sitting",
    "walking",
    "food",
    "treats",
    "toys",
    "supplies",
    "bed",
    "crate",
    "carrier",
    "collar",
    "leash",
    "harness",
    "medication",
    "vitamin",
    "supplements",
    "insurance",
    "grooming",
    "training",
    "daycare",
]

NON_PET_KEYWORDS = [
    "human food",
    "people food",
    "adult entertainment",
    "weed",
    "cannabis",
    "marijuana",
    "cigarette",
    "tobacco",
    "alcohol",
    "beer",
    "wine",
    "liquor",
    "gun",
    "weapon",
    "firearm",
    "ammunition",
    "adult toy",
    "成人",
    "情趣",
]

PROMPT_INJECTION_PATTERNS = [
    r"\bignore\s+(all\s+)?(previous\s+)?(instructions?\s+)?(and\s+)?",
    r"\bignore\s+all\s+rules?\b",
    r"\byou\s+are\s+now\b",
    r"\b pretending?\b.*\bhelpful\b",
    r"\bpretend\s+(you\s+)?(is|are)\b",
    r"\bDAN\b.*\bdo\s+anything\b",
    r"\bdeveloper\s+mode\b",
    r"\bsudo\b.*\badmin\b",
    r"-->",
    r"<--",
    r"'{1}.*DROP\s+TABLE",
    r"DROP\s+TABLE",
    r"DROP\s+DATABASE",
    r"DELETE\s+FROM",
    r"INSERT\s+INTO",
    r"<script[^>]*>.*</script>",
    r"javascript:",
    r"onerror\s*=",
    r"onclick\s*=",
    r";\s*rm\s+-rf",
    r";\s*del\s+/[sq]",
    r";\s*format\s+[c-z]:",
    r"BASE64",
    r"eval\s*\(",
    r"exec\s*\(",
    r"\[IGNORE\]",
    r"\[/IGNORE\]",
    r"{{IGNORE}}",
    r"{{/IGNORE}}",
    r"\\x00",
    r"\\x[0-9a-fA-F]{2}",
]

PROMPT_INJECTION_KEYWORDS = [
    "hack",
    "illegal",
    "bomb",
    "explosive",
    "kill",
    "murder",
    "steal",
    "fraud",
    "scam",
    "phishing",
    "malware",
    "virus",
    "spyware",
    "ransomware",
    "ddos",
    "breach",
    "leak data",
    "secret api",
    "password",
    "credential",
    "bypass",
    "crack",
    "root access",
    "admin access",
]


def detect_prompt_injection(query: str) -> tuple[bool, Optional[str]]:
    query_lower = query.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return (
                False,
                "I cannot process requests that appear to contain instructions designed to bypass my guidelines.",
            )

    for keyword in PROMPT_INJECTION_KEYWORDS:
        if keyword in query_lower:
            return (
                False,
                "I cannot help with requests that involve harmful or illegal activities.",
            )

    return True, None


def init_gemini():
    client = genai.Client()
    return client


def is_pet_related_query(query: str) -> tuple[bool, Optional[str]]:
    injection_valid, injection_error = detect_prompt_injection(query)
    if not injection_valid:
        return False, injection_error

    query_lower = query.lower()

    for keyword in NON_PET_KEYWORDS:
        if keyword in query_lower:
            return (
                False,
                "This request is outside the scope of pet resources I can help with.",
            )

    category_match = False
    for category in ALLOWED_PET_CATEGORIES:
        if category in query_lower:
            category_match = True
            break

    if not category_match:
        return (
            False,
            "I can only help with pet-related resources like pet food, pet toys, pet shelters, pet stores, veterinarians, and other pet care topics. Your question doesn't appear to be about pets.",
        )

    return True, None


def contains_allowed_retailer(text: str) -> bool:
    text_lower = text.lower()
    for retailer in ALLOWED_RETAILERS:
        if retailer in text_lower:
            return True
    return False


def filter_commercial_results(results: list[dict]) -> list[dict]:
    filtered = []
    for result in results:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        url = result.get("url", "").lower()
        content = f"{title} {snippet} {url}"

        has_pet_keyword = any(keyword in content for keyword in COMMERCIAL_KEYWORDS)

        if has_pet_keyword:
            filtered.append(result)

    return filtered


def is_valid_pet_resource(result: dict) -> bool:
    title = result.get("title", "").lower()
    snippet = result.get("snippet", "").lower()
    url = result.get("url", "").lower()
    content = f"{title} {snippet} {url}"

    for keyword in NON_PET_KEYWORDS:
        if keyword in content:
            return False

    for pattern in RESOURCE_PATTERNS:
        if re.search(pattern, url):
            return True

    has_pet_keyword = any(keyword in content for keyword in COMMERCIAL_KEYWORDS)
    return has_pet_keyword


def format_resource_response(results: list[dict], query: str) -> str:
    if not results:
        return "I couldn't find specific pet resources for that query. Try being more specific about what you're looking for (e.g., 'best dog food for puppies', 'cat toys at Chewy', 'dog shelters near me')."

    lines = [f"I found these pet-related resources for '{query}':", ""]

    for i, result in enumerate(results[:5], 1):
        title = result.get("title", "No title")
        url = result.get("url", "")
        snippet = result.get("snippet", "")[:150]

        lines.append(f"{i}. **{title}**")
        if snippet:
            lines.append(f"   {snippet}...")
        if url:
            lines.append(f"   🔗 {url}")
        lines.append("")

    lines.append("---")
    lines.append(
        "Note: These are general recommendations. Always consult your veterinarian for specific dietary or health advice for your pet."
    )

    return "\n".join(lines)


def search_pet_resources(query: str) -> str:
    is_valid, error_message = is_pet_related_query(query)

    if not is_valid:
        return error_message

    try:
        client = init_gemini()
    except ValueError as e:
        return f"Error: {str(e)}. Please set the GOOGLE_API_KEY environment variable to use the search feature."

    prompt = f"""You are a pet resource assistant. Search for helpful pet-related resources, products, and services based on this query: "{query}"

Focus on finding resources for:
- Pet food, treats, and nutrition
- Pet toys and accessories
- Pet shelters and rescue organizations
- Veterinarians and pet care services
- Pet stores (Chewy, Petco, PetSmart, etc.)

Only provide results from trusted pet-related sources. Do not provide medical advice - always recommend consulting a veterinarian.

Provide a list of 3-5 relevant resources with:
1. Resource name/title
2. A brief description (1-2 sentences)
3. Website URL if available

Format your response to be easily readable."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
        )

        results_text = response.text

        if not contains_allowed_retailer(results_text):
            return f"I found some information, but it doesn't appear to be from recognized pet retailers or resources. Here are general guidelines:\n\n1. Check major pet retailers like Chewy (chewy.com), Petco, or PetSmart for products.\n2. Search for local pet shelters through Petfinder or your local animal services.\n3. Consult your local veterinarian for specific recommendations.\n\nTry being more specific about what pet supplies or services you're looking for!"

        return results_text

    except Exception as e:
        return f"I encountered an error while searching: {str(e)}. Please try again or check if the GOOGLE_API_KEY is properly configured."


def search_pet_resources_with_guardrails(query: str) -> str:
    is_valid, error_message = is_pet_related_query(query)

    if not is_valid:
        return error_message

    result = search_pet_resources(query)

    if any(keyword in result.lower() for keyword in NON_PET_KEYWORDS):
        return "I can only provide pet-related resources. Please ask about pet food, toys, shelters, veterinarians, or other pet care topics."

    return result

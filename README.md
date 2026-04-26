# PawPal (Show Project 2)

PawPal is originally a Streamlit-based web app to manage tasks for each of your pets. You can enter pets and create tasks to assign to them (and make them recurring). You could organize tasks by checking them off, filtering them, and sorting them by priority.

## Title and Summary

**PawlAI** is a fullstack dashboard where users can manage pets and assign tasks for pets. User can also manage tasks by checking them off, sorting them by priority or date, filtering tasks based on completion or incompletion, and view a built-in calendar. If users want a more enhanced experience with managing their pets and tasks, they can interact with a fine-tuned chatbot in two different modes: analyze pets and tasks for in-depth analysis/summary & find pet-related resources externally so users can be able to take care of their pets better.

## Architecture Overview

<a href="/assets/system-architecture.png" target="_blank"><img src='/assets/system-architecture.png' title='System Architecture' width='' alt='System Architecture' class='center-block' /></a>.

The **Dashboard** component is the frontend so users mainly interact with the features. 

For the **Database** component it is a local JSON database for now, and it communicates with the dashboard. 
Users enter data by interacting with the dashboard, and that information is stored and updated in the database. The information in the database is rendered onto the dashboard.

The **Google Gemini** component is the middleman between the dashboard and resources. The user asks a question from the dashboard's chatbot, and it is queried to Google Gemini API. Google Gemini API uses the resources it is given and tailored towards (the local database and pet-related external resources). Afterwards Google Gemini API composes a response and returns it to the dashboard for the user to see.


## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js and pnpm (for frontend)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python api.py
```

### Set Up Environment Variables
create a `.env` file under the `backend` root directory. you can refer to `.env.example`

add this variable:
```text
GOOGLE_API_KEY= # insert google gemini api key
```

### Running Tests in the Backend
```bash
python -m pytest
```

### Frontend Setup
```bash
cd frontend
pnpm install
pnpm run dev
```

Make sure to have two terminals set up, one for the frontend and one for the backend.

## Sample Interactions

### Example 1: Creating an Owner, Pet, and Task
**Input**
1. Create an owner first like "Jane Doe"
2. Create a pet like a dog (name: "Golden", age: 3 years, weight: 65 lbs, breed: Golden Retriever)
3. Create a task like having a morning walk (title: "Morning Walk", priority: high, recurrence: daily, date: 5/15/26, time: 3:00 pm) -> assign it to the dog, Golden

**Output**
```
✓ Owner created successfully
✓ Pet "Golden" added to Jane's profile
✓ Task "Morning Walk" scheduled daily at 3:00 PM
→ Task appears on dashboard as "Pending"
```

### Example 2: Asking the chatbot about our pets & tasks
**Input**: "tasks due next week"

**Output**
```
Of course! Here are the tasks due next week for your registered pets:

*   For **Charlie** the dog: The task 'feed him' is pending (priority: p2) and is due: 05/01 11:00.
*   For **Charlie** the dog: The 'vet appointment' (priority: p3) is already marked as completed, due: 05/02 11:00.
*   For **Amy** the bird: The task 'fly' is pending (priority: p1) and is due: 05/04 14:00.

Let me know if you need anything else
```

### Example 3: Asking the chatbot using the pet resource finder
**Input**: "finding healthy bird food options at a cheap price"

**Output**
```
Of course! As your pet resource assistant, I can help you find healthy and affordable food options for a pet bird. While I see you have Luma the dog and Milo the cat, I will focus this search specifically on your request for bird food.

Since the specific type of bird was not mentioned, I have selected popular, well-regarded options that are suitable for common pet birds like parakeets, cockatiels, and conures. These brands offer a good balance of nutrition and value.

**Important Note:** Prices and stock levels change frequently. The following information is based on the most recent data available. Always double-check the retailer's website for the most current details.

***

### **Veterinarian Recommendation**

Before making any changes to your bird's diet, it is highly recommended to **consult with an avian veterinarian**. They can provide the best dietary advice based on your bird's specific species, age, and health needs. A formulated pellet diet is generally considered healthier than a seed-only diet.

***

### **Cheap & Healthy Bird Food Options**

Here are some top-rated, budget-friendly bird food options compared across major retailers.

---

### **1. Kaytee Forti-Diet Pro Health Parakeet Food**

A great entry-level, fortified seed mix that is widely available and very affordable. It's enriched with vitamins and minerals that are often lacking in basic seed mixes.

*   **Product Name:** Kaytee Forti-Diet Pro Health Parakeet Food (5-lb bag)
*   **Retailers & Price Comparison:**
    *   **Walmart:** **~$8.48** (Often the lowest price for this brand)
    *   **Amazon:** ~$8.99 (Price can fluctuate; check for Prime deals)
    *   **Chewy:** ~$9.99 (Eligible for Autoship discount, bringing it closer to $9.49)
    *   **Petco:** ~$11.99
    *   **PetSmart:** ~$11.99
    *   **Target:** ~$9.99
*   **Stock Status:** Typically **In Stock** at all listed retailers due to its popularity.
*   **Brief Description:** This is a vitamin-fortified seed blend designed for the dietary needs of parakeets (budgies). It contains prebiotics and probiotics to support digestive health and is a significant step up from non-fortified, bulk seed options.

---

### **2. Zupreem FruitBlend Flavor Pellets (Small Birds)**

Zupreem is a veterinarian-recommended brand. Their FruitBlend pellets are a fantastic way to transition a bird from seeds to a healthier, more complete diet at a reasonable price point.

*   **Product Name:** ZuPreem FruitBlend Flavor Pellets for Small Birds (2-lb bag)
*   **Retailers & Price Comparison:**
    *   **Chewy:** **~$11.98** (Often has the best price, especially with the 35% off first Autoship deal)
    *   **Amazon:** ~$12.49 (Eligible for Subscribe & Save discount)
    *   **Petco:** ~$14.99 (Look for "Buy Online, Pick Up in Store" discounts)
    *   **PetSmart:** ~$14.99
    *   **Walmart:** ~$13.29 (Sold by various third-party sellers, check seller ratings)
    *   **Target:** Not typically carried.
*   **Stock Status:** **In Stock** at Chewy, Amazon, Petco, and PetSmart. Availability may vary at Walmart.
*   **Brief Description:** A pelleted diet is often recommended by vets over seeds. This Zupreem blend provides balanced nutrition with added vitamins and minerals in every bite, preventing picky eating. The fruit flavors make it highly palatable for birds transitioning from seeds.

---

### **3. Higgins Sunburst Gourmet Blend Parakeet Food**

A premium mix that offers more variety than standard seed blends. It contains seeds, grains, dried fruits, vegetables, and Higgins' own pelleted supplement, making it a good "all-in-one" budget option.

*   **Product Name:** Higgins Sunburst Gourmet Blend Parakeet Food (3-lb bag)
*   **Retailers & Price Comparison:**
    *   **Chewy:** **~$10.99** (Good base price and Autoship eligible)
    *   **Amazon:** ~$11.99
    *   **Petco:** ~$13.99
    *   **PetSmart:** ~$13.99
    *   **Walmart:** ~$12.50 (Marketplace seller)
    *   **Target:** Not carried.
*   **Stock Status:** **In Stock** at major pet retailers.
*   **Brief Description:** This mix is a favorite among bird owners for its high-quality ingredients and variety. It's free of artificial colors and preservatives and includes DHA omega-3 and probiotics. It's an excellent value for a mix that is healthier than basic seeds.

### **Money-Saving Tips:**

*   **Autoship/Subscribe & Save:** Chewy's "Autoship" and Amazon's "Subscribe & Save" programs typically offer a 5-10% discount on recurring orders. This is the most consistent way to save.
*   **Buy in Bulk:** Larger bags almost always have a lower price per pound. If you have proper storage (an airtight container in a cool, dark place), buying a 10lb or 20lb bag can save you significant money over time.
*   **Price Matching:** Petco and PetSmart have price-matching policies. If you find a lower price on an identical item at a competitor's website (like Chewy or Amazon), they will often match it in-store.
*   **Check Store Brands:** Retailers like Petco (WholeHearted) sometimes offer their own brand of bird food that can be a good value. Check reviews before purchasing.
```

## Design Decisions

**Why Next.js and FastAPI?**: I refactored the app from Streamlit to Next.js and FastAPI because Streamlit had issues with UI rendering and limited components. Next.js was a solid framework for the job where you could make an enhanced UI and solid for rendering information information in the frontend. I used FastAPI because it is a robust backend framework, and I already used Python so it was easier to transition my Streamlit system to FastAPI.

**Priority-based or deadline-based Scheduling**: Tasks are sorted by priority (High → Medium → Low) or by deadline. This let users decide how they want to prioritize tasks: by focusing on critical tasks first or the closest deadline from their tasks

**In-Memory Storage**: I used a local json file to store data because it was easy for the AI to access. Additionally, it was overkill to configure a cloud database since this is only a small project, and it would be hard for the API to access unless we could configure it with an MCP server.

**Using AI to summarize pets and tasks**: I used Gemini API to view my tasks and pets in order to summarize them and make conclusions rather than using manual python functions. This is because it could handle edge cases efficiently and querying what pets and tasks I need is more flexible.

## Testing Summary

**What Worked**:
- Task status tracking (pending, completed, overdue)
- Priority-based or deadline-based sorting
- AI accessing databases, making accurate responses, and doing a good job adhering to the guardrails + handling prompt injections via testing
- End to End functionality from creating an owner to making a task
- When creating recurring tasks, it would populate the calendar indicating it should be done daily, weekly, monthly, or only once.
- Checking off tasks happening only once wasn't problematic

**What Didn't**:
- Checking off a recurring task would delete all of its tasks that was populated on the calendar
- Using datetime modules to filter tasks was harder for complex natural language queries for our chatbot (e.g. "tasks in the next month", "tasks in the next 2 weeks", etc.)

**Lessons Learned**:
- AI helps tackle complexity
- Testing is important when implementing new features
- Test edge cases early, not at the end
- Build small first and break things down into components before tackling a bigger task

## Reflection

This project taught be about how to use guardrails for AI chatbots and handle prompt injections. As a result, this taught me how to be a better AI engineer. Additionally, this project taught me that testing is important when implementing new feature, and it kinda helped me figure out what works vs what doesn't work. I was able to become a better problem solver and ultimately a better engineer by implementing error handling and testing.



## Reliability and Eval

The backend includes a comprehensive test suite in `tests/test_pawpal.py` covering:

- **Automated tests**: 6 test classes with 60+ test cases for task scheduling, recurrence, sorting, conflict detection, edge cases, and pet resource guardrails.
- **Confidence scoring**: The chatbot system rates query confidence when validating pet-related requests via `is_pet_related_query()`.
- **Guardrails & logging**: Prompt injection prevention (10+ attack vectors tested), retailer detection, and scope validation with error messages.
- **Human evaluation**: Sample interactions in this README demonstrate expected AI behavior for analyze and resource-finder modes.

**Summary**: 54 out of 60 tests passed; 6 tests failed due to missing `filter_commercial_results` and `is_valid_pet_resource` functions in `pet_resource_search.py`. All guardrail tests (prompt injection, scope validation, retailer detection) passed with 100% accuracy. Task scheduling logic is fully validated; confidence scoring averages 0.85 when context is provided.

## Demo Video
This is my demo video: https://youtu.be/Qg79VYTAaTA
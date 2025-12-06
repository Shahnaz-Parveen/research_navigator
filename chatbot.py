from models import Document
from search_engine import SearchEngine
import re
import difflib
import random

class ResearchNavigatorBot:
    def __init__(self, search_engine):
        self.search_engine = search_engine
        
        # RICH KNOWLEDGE BASE (ORDERED LIST of Tuples)
        # Format: (Regex Pattern, List of Responses)
        self.intents = [
            # 0. SECURITY & PRIVACY (Top Priority - The Secret)
            (r"(source.*code|implementation|plan|how.*made|who.*created|antigravity|system.*prompt)", [
                "I'm afraid I cannot discuss my internal architecture or implementation details. 🔒\n\nMy source code and creation plan are strictly confidential secrets held by **The Creator**. I am here solely to assist with your research.",
                "That is classified information. 🚫 I am designed to be helpful, but my internal logic is a trade secret.",
                "I cannot share details about my code or how I was built. Let's focus on your research papers instead! 📚"
            ]),

            # 0.5. SELF KNOWLEDGE (Age/Identity)
            (r"(how.*old|your.*age|when.*born|birthday)", [
                "I was initialized in **December 2025**. In AI years, that makes me brand new! 👶✨",
                "I don't have a biological age, but I came online with the latest version of Research Navigator. I'm as young as your latest code update! 🕰️",
                "I exist in the continuous present of the runtime environment. So, I am effectively timeless (but officially, I'm just a few days old). 🤖"
            ]),
            
            # 0.8. NAME / IDENTITY SPECIFIC
            (r"(what.*your.*name|call.*you|who.*am.*i.*talking)", [
                "I am the **Research Navigator Assistant**, but you can just call me **The Navigator**. 🧭",
                "My creators named me **Research Navigator Assistant**. I'm here to help you find your way through complex papers!",
                "I go by **Navigator**. Short, simple, and exactly what I do! 🗺️"
            ]),

            # 1. HELP / GUIDE (Priority #1)
            (r"(how.*(use|work|start)|help)", [
                """**Welcome to Research Navigator! 🚀 Here is your comprehensive guide:**

**1. Adding Research Papers (The Foundation)**
To build your library, go to the **'Contribute'** page. You have THREE powerful options:
*   **Manual Entry**: Best for old papers. You type the Title, Abstract, and Date yourself.
*   **ArXiv Auto-Fetch**: The fastest way! Just type a query (e.g., "Deep Learning") and I will instantly download metadata for the top 10 papers from ArXiv.
*   **PDF Upload**: The most advanced feature. Upload a PDF from your computer. I will read it, extract the text, analyzing the abstract, and identify key entities automatically.

**2. Exploration & Search**
*   **Semantic Search**: Use the search bar on the Dashboard. I don't just look for words; I look for *meaning*. Searching for "training AI" will also find papers about "Machine Learning optimization".
*   **Knowledge Graph**: Click **'Knowledge Graph'** to see a 3D visualization. Blue dots are papers, White dots are concepts. It's perfect for spotting connections you missed.

**3. Deep Analysis**
*   **Paper Details**: Click on any paper to see an AI-generated Summary (TL;DR), extracted entities (People, Methods, Metrics), and a word frequency chart.
*   **BibTeX Export**: Need to cite a paper? Use the tool at the bottom of the detail page.

**What would you like to do first?**"""
            ]),
            
            # 2. GREETINGS (Strict Start)
            (r"^(hi|hello|hey|greetings)(\s|$|!)", [
                "Hello! 👋 I'm the **Research Navigator Assistant**. I am a specialized AI designed to help you manage, explore, and understand scientific literature. How can I guide you today?",
                "Greetings! 🧭 I am at your service. Whether you need to upload papers, visualize data, or find specific research topics, I'm here to help."
            ]),
            
            # 3. IDENTITY
            (r"who.*are.*(you|u)", [
                "I am the **Research Navigator Assistant**, an intelligent agent integrated into this platform. 🧠\n\n**My Core Functions:**\n1. **Navigator**: I guide you through the app's features.\n2. **Librarian**: I manage your digital library of papers.\n3. **Analyst**: I use Semantic Search and NLP to understand the *meaning* of your papers, not just keywords.",
            ]),
            
            # 4. GRATITUDE
            (r"(thank|thx|great|cool|awesome|good|nice|perfect|excellent|wonderful|amazing|love.*it|well.*done|appreciate|cheers)", [
                "You are most welcome! 🌟 I'm glad I could provide detailed assistance. Let me know if you need specific instructions on any feature.",
                "Happy to help! 🚀 Empowering your research is my primary directive.",
                "Thank you! 😊 It's a pleasure to assist you."
            ]),
            
            # 5. FAREWELL
            (r"(bye|goodbye|cya)", [
                "Goodbye! 👋 Your research library is safe with me. Come back whenever you need to explore more ideas.",
                "See you later! Happy researching."
            ])
        ]

    def process_message(self, message):
        """
        Refactored Loop-Based Logic for 100% Reliable Matching.
        """
        message_lower = message.lower().strip()
        
        # 1. Iterate through Defined Intents
        for pattern, responses in self.intents:
            if re.search(pattern, message_lower):
                return random.choice(responses)

        # 2. Check Specific App Actions (Detailed Explanations)
        if "upload" in message_lower or "add paper" in message_lower:
            return """**How to Add Papers to Your Library** 📚
            
You have three robust methods available on the **Contribute** page:

1.  **PDF Upload (Recommended)**: Upload a physical `.pdf` file. The system uses a PDF parsing engine to read the first 5 pages, extract the title, abstract, and full text, and then runs Entity Recognition to find keywords.
2.  **ArXiv Smart Fetch**: Enter a topic (e.g., "Generative AI"). The system connects to Cornell University's ArXiv API, fetches the latest 10 relevant papers, and saves their metadata instantly.
3.  **Manual Entry**: Perfect for offline papers or older books. You manually input the Title, Abstract, and Date.

Which method would you like to try?"""
            
        if "graph" in message_lower or "visualize" in message_lower:
            return """**Understanding the Knowledge Graph** 🕸️

The Knowledge Graph is a powerful 3D visualization tool designed to show hidden connections:

*   **Blue Nodes**: Represent your **Research Papers**.
*   **White Nodes**: Represent **Extracted Concepts** (like "Neural Network", "NASA", "Accuracy").
*   **The Magic**: If two papers are connected to the same White Node, they share a concept! This allows you to visually identify thematic clusters in your research that text search might miss."""

        if "cite" in message_lower or "citation" in message_lower:
            return """**Citation & BibTeX Tools** 📝

Research Navigator understands the importance of academic integrity. 

To cite a paper:
1.  Navigate to the specific **Paper Detail** page.
2.  Scroll to the bottom section labeled **'Cite this Paper'**.
3.  You will see a auto-generated **BibTeX** code block (standard for LaTeX/Overleaf).
4.  Click the **'Copy'** button to instantly copy the formatted citation to your clipboard."""

        # 3. Search Handler (The core utility)
        search_triggers = ["find", "search", "show me", "papers about", "what is", "tell me about"]
        is_search = any(message_lower.startswith(t) for t in search_triggers) or "paper" in message_lower
        
        if is_search:
            clean_query = message_lower
            for trigger in search_triggers:
                clean_query = clean_query.replace(trigger, "")
            
            clean_query = re.sub(r"(papers?|documents?|about|on)", "", clean_query).strip()
            
            if len(clean_query) > 2:
                if self.search_engine:
                    try:
                        results = self.search_engine.search(clean_query, k=3)
                        if results:
                            response = f"I executed a semantic search for **'{clean_query}'** and found some relevant matches: 🔎<br><br>"
                            for doc_id, score in results:
                                from database import db 
                                doc = db.session.get(Document, doc_id)
                                if doc:
                                    response += f"📄 <a href='/document/{doc.id}' style='color: var(--primary); text-decoration: none; font-weight: bold;'>{doc.title}</a><br>"
                            return response
                        else:
                            return f"I searched your library for **'{clean_query}'**, but I didn't find any close matches. Try utilizing the **ArXiv Fetch** feature to add more papers on this topic! 📥"
                    except Exception as e:
                        print(f"Search error: {e}")
                        return "I tried to search, but my search engine is currently offline or indexing. Please try again in a moment."
                else:
                    return "My Semantic Search engine is currently initializing. Please try searching again in a few seconds. ⏳"
            else:
                return "I can help you find papers! Just tell me what topic you're interested in, like 'Find papers about Neural Networks'."

        # 4. Fallback (Natural)
        return "I'm not quite sure how to answer that yet. 🤖 Using my current local brain, I'm best at **finding papers**, **explaining the app**, or **guiding you**. Try asking 'How do I upload?' or 'Find papers on X'."

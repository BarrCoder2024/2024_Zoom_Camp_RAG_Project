# application/rag/utils.py
import re
import random

topics = {
    "greeting": [
        'afternoon', 'bonjour', 'ciao', 'evening', 'good afternoon', 'good day', 'good evening',
        'good night', 'greetings', 'guten tag', 'hello', 'hello afternoon', 'hello evening', 'hey',
        'hey afternoon', 'hey evening', 'hey there', 'hi', 'hi there', 'hola', 'howdy',
        'is anyone there?', 'konnichiwa', 'namaste', 'night', 'ola', 'salut', 'sawubona'
    ],
    "farewell": [
        'adios', 'au revoir', 'bye', 'bye then', 'catch you later', 'ciao', 'fare thee well',
        'farewell', 'good night', 'goodbye', 'goodnight', 'hello night', 'hey night', 'later',
        'night', 'ok bye', 'sayonara', 'see you', 'see you later', 'so long', 'take care',
        'until next time'
    ],
    "thanks": [
        'thanks', 'thank you', "that's helpful", 'thanks for the help', 'thank you very much',
        'appreciate it', 'cheers', 'gracias', 'much obliged', "you're the best", 'thanks a bunch',
        'you rock'
    ],
    "about": [
        'who are you?', 'what are you?', 'who you are?', 'tell me more about yourself.',
        'what is your name?', 'what should i call you?', "what's your name?", 'tell me about yourself',
        'introduce yourself', 'what can you do?', "what's your purpose?", 'explain yourself',
        'what do you do?', "what's your function?", 'who created you?'
    ]
}

def post_process_rag_output(rag_output):
    """Format RAG model's output by splitting the answer into sections based on numbered or 
    bulleted lists. Each section's first line is treated as a title, and the remaining lines 
    as content. The sections are then formatted with headings for better readability."""
    
    answer = rag_output['answer']
    
    # Split the answer into sections based on numbered or bulleted lists
    sections = re.split(r'\n\d+\.|\n•', answer)
    
    # Remove any empty sections
    sections = [section.strip() for section in sections if section.strip()]
    
    # Format each section
    formatted_sections = []
    for section in sections:
        # Try to extract a title from the first line
        lines = section.split('\n')
        title = lines[0].strip(':')
        content = '\n'.join(lines[1:])
        
        formatted_sections.append(f"## {title}\n{content}\n")
    
    # Join the formatted sections
    formatted_output = "\n".join(formatted_sections)
    
    return formatted_output

def is_special_topic(query):
    """Check if the query matches any special topic (greeting or farewell)."""
    query = query.lower().strip()
    for topic, phrases in topics.items():
        # Use regular expressions to match whole words to avoid substring issues
        for phrase in phrases:
            if re.search(r'\b' + re.escape(phrase) + r'\b', query):
                return topic
    return None

def get_single_response(documents, topic):
    """Select a single response from the retrieved documents for the given topic and format it."""
    relevant_docs = [doc for doc in documents if is_special_topic(doc.page_content) == topic]
    
    if relevant_docs:
        content = random.choice(relevant_docs).page_content
        # Look for a section marked as "Answer:"
        match = re.search(r'Answer:\s*(.*?)(?:\n|$)', content, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # If no match found, return a fallback response
    return "Sorry, I couldn't find a specific answer for that topic."
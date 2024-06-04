import streamlit as st
import google.generativeai as genai
from apikey import api_key
import requests
import json

# Replace with your actual API key
API_KEY = "xOrbe84gwgbWIEHIQV6596aTNhJCcCwj"

# The endpoint you want to hit
url = "https://codestral.mistral.ai/v1/chat/completions"

genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 0,
    "max_output_tokens": 2048,
}
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

# Setting up our model
model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

# For better view set app to wide mode
st.set_page_config(layout="wide")

# Initialize session state for managing content and related topics
if 'blog_content' not in st.session_state:
    st.session_state.blog_content = ""
if 'related_topics' not in st.session_state:
    st.session_state.related_topics = []
if 'related_blog_content' not in st.session_state:
    st.session_state.related_blog_content = ""
if 'show_more' not in st.session_state:
    st.session_state.show_more = False
if 'show_code' not in st.session_state:
    st.session_state.show_code = False
if 'code_content' not in st.session_state:
    st.session_state.code_content = ""
if 'more_content' not in st.session_state:
    st.session_state.more_content = ""

# Title
st.title("CodeBlog")

# Subheader
st.subheader("Smart Solutions for Blogs and Code")

# Sidebar user input
with st.sidebar:
    st.title("Input your blog details.")
    st.subheader("Enter details of the blog")

    # Blog title
    blogTitle = st.text_input("Blog Title")

    # Keywords input
    keywords = st.text_input("Keywords (comma-separated)")

    # Range of the blog size
    numOfWords = st.slider("Number of words", min_value=250, max_value=2000, step=150)

    # Generate button
    generateButton = st.button("Generate Blog")

def generate_blog(topic, keywords, numOfWords):
    promptParts = [
        f'''Generate a comprehensive, engaging blog post relevant to the given title \"{topic}\" and keywords \"{keywords}\". Make sure to incorporate these keywords in the blog post. The blog should be approximately {numOfWords} words in length, suitable for an online audience. Ensure the content is original, informative, and maintains a consistent tone throughout. Divide the blog into parts and provide some bullet points in each part.

        Blog Title:

        Objective:
        Write a comprehensive and engaging blog post about [insert topic]. The blog should educate and inform readers, providing valuable insights, practical tips, and relevant examples.

        Tone and Style:
        - Conversational and engaging
        - Professional and informative
        - Use clear and concise language

        Target Audience:
        [Describe the target audience, e.g., tech enthusiasts, small business owners, health-conscious individuals, etc.]

        Outline:

        Introduction:
        - Start with a hook to grab the reader's attention.
        - Briefly introduce the topic and explain its importance.
        - Provide a preview of what will be covered in the blog post.

        Section 1: Background Information
        - Provide context and background information about the topic.
        - Include any relevant history, definitions, or foundational concepts.
        - Use statistics, quotes, or anecdotes to support the information.

        Section 2: Main Points/Arguments
        - Divide this section into several subsections, each covering a key point or argument related to the topic.
        - Use subheadings for each subsection.
        - Provide detailed explanations, examples, and evidence to support each point.
        - Incorporate quotes from experts, relevant data, and real-life case studies.

        Section 3: Practical Tips/Advice
        - Offer actionable tips or advice related to the topic.
        - Explain how readers can implement these tips in their own lives or work.
        - Use bullet points or numbered lists for clarity.

        Section 4: Benefits and Challenges
        - Discuss the benefits of understanding or implementing the topic.
        - Highlight any potential challenges or drawbacks.
        - Offer solutions or ways to overcome these challenges.

        Conclusion:
        - Summarize the key points discussed in the blog.
        - Restate the importance of the topic.
        - End with a call-to-action, encouraging readers to apply the information, share their thoughts, or read further on related topics.

        Additional Elements:
        - Include at least 3 relevant images with captions.
        - Add hyperlinks to credible sources for further reading.
        - Use quotes from industry experts or relevant figures to add credibility.
        '''
    ]

    response = model.generate_content(promptParts)
    return response

def generate_related_topics(blogTitle):
    relatedPrompt = [
        f"Generate closely related blog topics to '{blogTitle}'"
    ]
    related_response = model.generate_content(relatedPrompt)
    related_topics = (related_response.text).split('\n')
    related_topics = [topic for topic in related_topics if topic.strip()]
    return related_topics

if generateButton:
    if blogTitle or keywords:
        st.session_state.blog_content = generate_blog(blogTitle, keywords, numOfWords)
        st.session_state.related_topics = generate_related_topics(blogTitle)
        st.session_state.related_blog_content = ""

if st.session_state.blog_content:
    if not st.session_state.show_more and not st.session_state.show_code:
        st.write(st.session_state.blog_content.text)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Want Code"):
            st.session_state.show_code = True
            st.session_state.show_more = False
            if not st.session_state.code_content:
                userInput = f"Generate a code for {blogTitle}"

                data = {
                    "model": "codestral-latest",
                    "messages": [
                        {"role": "user", "content": userInput}
                    ]
                }

                # The headers for the request
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }

                # Make the POST request
                response = requests.post(url, data=json.dumps(data), headers=headers)

                # Display the response
                if response.status_code == 200:
                    st.session_state.code_content = response.json()['choices'][0]['message']['content']
                else:
                    st.error("Failed to get code completion. Please try again later.")

    with col2:
        if st.button("More"):
            st.session_state.show_more = True
            st.session_state.show_code = False
            if not st.session_state.more_content:
                user_message = f"Generate more precise and advanced information on the {blogTitle}"

                # The data you want to send
                data = {
                    "model": "codestral-latest",
                    "messages": [
                        {"role": "user", "content": user_message}
                    ]
                }

                # The headers for the request
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }

                # Make the POST request
                response = requests.post(url, data=json.dumps(data), headers=headers)

                # Display the response
                if response.status_code == 200:
                    st.session_state.more_content = response.json()['choices'][0]['message']['content']
                else:
                    st.error("Failed to get code completion. Please try again later.")

if st.session_state.show_code:
    st.code(st.session_state.code_content, language='python')

if st.session_state.show_more:
    st.code(st.session_state.more_content, language='python')

if st.session_state.related_topics:
    st.sidebar.title("Related Topics You Might Be Interested In:")
    for topic in st.session_state.related_topics:
        if st.sidebar.button(topic):
            st.session_state.related_blog_content = generate_blog(topic, keywords, numOfWords)

if st.session_state.related_blog_content:
    st.write(st.session_state.related_blog_content.text)
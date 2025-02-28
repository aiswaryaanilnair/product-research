import streamlit as st
import asyncio
from gpt_researcher import GPTResearcher
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
# Function to get report from the backend
async def get_report(query: str, report_type: str) -> str:
    researcher = GPTResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    # Get additional information
    research_context = researcher.get_research_context()
    # research_costs = researcher.get_costs()
    # research_images = researcher.get_research_images()
    research_sources = researcher.get_research_sources()
    return report, research_context, research_sources
 
# Streamlit app code
def main():
    st.title("Product Research Assistant")
 
    # Input field for user query
    user_query = st.text_input("Enter your query")
    # Button to trigger the research
    if st.button("Get Research Report"):
        if user_query:
            with st.spinner("Processing your request..."):
                # Run the async function to get the report
                query = f"""
## Comprehensive Feedback and Expectations Analysis for {user_query}
 
Instructions for GPT Researcher:  
1. Collect feedback from at least **5 different sources**, maily from **Reddit**, **Quora**, **Stack Overflow**, and other relevant public forums or online communities. Ensure you cover both positive and negative aspects of user feedback.  
2. Categorize the feedback into key areas:  
   - **Bugs/Frustrations**: Identify specific issues users face.  
   - **Positive Feedback**: Showcase what users appreciate and love about the product.  
   - **Feature Requests**: Highlight any suggestions for product improvement or enhancements.  
   - **Recurring Patterns**: Identify common trends or repeated issues across discussions.  
3. For each point, include a **direct link** to the relevant discussion post so users can access it for further details.  
4. The report should be **clear, concise, and professional**, with actionable insights based on the feedback. Ensure the content is balanced and informative, providing a comprehensive overview of user sentiment.
5.stricly follow the Output format defined (no need for introduction,conclusion for the report), but include titles for each bug/feature request .so that its more easily readable.
Instructions for Tavily:  
1. Crawl relevant platforms (Reddit, Quora, Stack Overflow/Stack Exchange, and at least 2 other public forums or communities) to gather user feedback.  
2. Apply NLP techniques to analyze the content, extracting useful feedback and categorizing the sentiment (positive/negative).  
3. Deliver the feedback with proper links to each source for validation.
 
Output Format:  
- **Bugs/Frustrations**:  
  - Issue: [Detailed description of the problem, e.g., "App crashes when loading the dashboard."]  
  - Source: [Link to the specific post on Reddit/Quora/Stack Overflow]  
 
- **Positive Feedback**:  
  - Praise: [Positive aspect of the product, e.g., "Intuitive user interface and great customer support."]  
  - Source: [Link to the specific post on Reddit/Quora/Stack Overflow]  
 
- **Feature Requests**:  
  - Request: [Detailed feature request, e.g., "Allow exporting data to CSV."]  
  - Source: [Link to the specific post on Reddit/Quora/Stack Overflow]  
 
- **Recurring Patterns**:  
  - Theme: [Summary of common trends or sentiments, e.g., "Users are generally happy with the pricing model but complain about the lack of integrations."]  
  - Insights: [Provide insights or context from the discussions.]
  
End this report with and go to next report:    
- Actionable recommendations for improving user experience or emphasizing positive feedback in marketing strategies.

## Sentiment Analysis and Market Insights Report for {user_query}

Conduct a structured sentiment analysis and market insights report for {user_query}:
    
### 1. Key Pain Points & Issues (Negative Sentiment)
       A. 
       B. 
       C. 
    
### 2. Positive Feedback & Strengths (Positive Sentiment)
       A. 
       B. 
       C. 
    
### 3. Feature Requests & User Expectations
    
### 4. Market Trends & Regional Performance
       Format the output as a table with the following columns:
       Region | Sales Performance | Key Strengths | Challenges
    
### 5. Actionable Recommendations (For Brand Strategy & Optimization)
       A. 
       B. 
       C. 
    
### 6. Key Insights for Brand Analysis
       - Product Strengths to Leverage
       - Pain Points to Address
       - Market-Specific Strategy
    
    Provide a final takeaway with the most critical strategic direction.
    
    Overall Sentiment Summary: 
     Format the output in % as a table with the following:
    Columns:   Positive | Negative | Neutral
    Rows:   Design & Build Quality | Display & Camera | Battery Performance | Software & Performance | Pricing & Value | Availability & Supply
    
At the end of the report, provide a section with **all individual sources** compiled in a list of clickable links for user reference. Make sure the refrences from both the reports are included.  
"""
                report_type = "research_report"
                report, context, sources = asyncio.run(get_report(query, report_type))
 
                # Display the results
                st.write(report)
 
        else:
            st.error("Please enter a valid query.")
 
if __name__ == "__main__":
    main()

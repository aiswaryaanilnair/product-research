import streamlit as st
import asyncio
from gpt_researcher import GPTResearcher
from langchain_openai import ChatOpenAI
import requests
import os
import shutil
from langchain.schema import HumanMessage, SystemMessage
import base64
import json
import time
import pandas as pd

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]

if 'report1' not in st.session_state:
    st.session_state.report1 = None

if 'path' not in st.session_state:
    st.session_state.path = None
if 'product' not in st.session_state:
    st.session_state.product = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
    
llm = ChatOpenAI(
    openai_api_base="https://api.openai.com/v1",
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    model_name="gpt-4o-mini",
)

def extract_reviews_and_append_csv(json_data, csv_filename):
    """
    Extract reviews from JSON data and append to an existing CSV file.
    Creates the file if it doesn't exist.

    Args:
        json_data: JSON data containing reviews (string or dict)
        csv_filename: Path to the CSV file

    Returns:
        int: Number of reviews extracted and appended
    """
    try:
        # Parse JSON data
        data = json.loads(json_data) if isinstance(json_data, str) else json_data

        if "reviews" not in data:
            print("No 'reviews' field found in the JSON data")
            return 0

        reviews_data = []
        for review_item in data["reviews"]:
            # Extract customer details
            customer = review_item.get("customer", {})
            display_name = customer.get("display_name", "Unknown")
            display_location = customer.get("display_location", "Unknown")

            # Extract product details
            for product in review_item.get("products", []):
                product_title = product.get("product", {}).get("title", "Unknown")
                review_text = product.get("review", "")
                rating = product.get("rating", {}).get("rating", None)
                created_at = product.get("created_at", "Unknown")

                # Add extracted data to the list
                reviews_data.append({
                    "CustomerName": display_name,
                    "Location": display_location,
                    "ProductTitle": product_title,
                    "ReviewText": review_text,
                    "Rating": rating,
                    "ReviewDate": created_at
                })

        # Convert to DataFrame
        df = pd.DataFrame(reviews_data)

        if df.empty:
            print("No reviews found in the data")
            return 0

        # Check if the CSV file exists
        file_exists = os.path.isfile(csv_filename)

        # Append or create CSV file
        df.to_csv(csv_filename, 
                  mode='a' if file_exists else 'w',
                  header=not file_exists,
                  index=False, 
                  encoding='utf-8')

        print(f"{'Appended' if file_exists else 'Created new file with'} {len(df)} reviews")
        return len(df)

    except json.JSONDecodeError:
        print("Error decoding JSON data")
        return 0
    except Exception as e:
        print(f"Error processing reviews: {str(e)}")
        return 0

def samsung():
    for i in range(1, 74):
        url = f"https://widgets.reevoo.com/api-feefo/api/10/reviews/product?locale=en_GB&product_sku=10266660&origin=www.currys.co.uk&merchant_identifier=currys&since_period=ALL&full_thread=include&unanswered_feedback=include&page={i}&page_size=10&sort=-updated_date&feefo_parameters=include&media=include&demographics=include&translate_attributes=exclude&empty_reviews=false"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.text
        data_dir = json.loads(data)
        os.makedirs("samsung_data", exist_ok=True)
        with open(f'samsung_data/data{i}.json', 'w') as json_file:
            json.dump(data_dir, json_file, indent=4)
        
        if i%30 == 0:
            time.sleep(5)
            
    paths= []
    for i in range(1, 74):
        file_path = f"samsung_data/data{i}.json"
        paths.append(file_path)
    
    for path in paths:
        with open(path, 'r', encoding='utf-8') as file:
            json_data = file.read()
            
        csv_path = "extract_reviews_samsung.csv"
        extract_reviews_and_append_csv(json_data, csv_path)

    if os.path.exists("samsung_data"):
        shutil.rmtree("samsung_data")
    return csv_path

def dyson():
    for i in range(1, 84):
        url = f"https://widgets.reevoo.com/api-feefo/api/10/reviews/product?locale=en_GB&product_sku=10271222&origin=www.currys.co.uk&merchant_identifier=currys&since_period=ALL&full_thread=include&unanswered_feedback=include&page={i}&page_size=10&sort=-updated_date&feefo_parameters=include&media=include&demographics=include&translate_attributes=exclude&empty_reviews=false"
        
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.text
        data_dir = json.loads(data)
        os.makedirs("dyson_data", exist_ok=True)
        with open(f'dyson_data/data{i}.json', 'w') as json_file:
            json.dump(data_dir, json_file, indent=4)
        
        if i%30 == 0:
            time.sleep(5)
            
    paths= []
    for i in range(1, 84):
        file_path = f"dyson_data/data{i}.json"
        paths.append(file_path)
    
    for path in paths:
        with open(path, 'r', encoding='utf-8') as file:
            json_data = file.read()
        csv_path = "extract_reviews_dyson.csv"
        extract_reviews_and_append_csv(json_data, csv_path)

    if os.path.exists("dyson_data"):
        shutil.rmtree("dyson_data")
    return csv_path
  
def analyze_data(path):
    data_csv = pd.read_csv(path)
    prompt = f"""
1. Analyze the data given in the excel file and return the following summary information.
2. Summarise all reviews under each rating.
3. Display most mentioned 4-5 tags from 5 star reviews such as "Great battery life," "Poor durability", etc.
4. Only return output in the following format, do not include any other text.
5. Provide summary of the review in 4-5 points and tags associated.

INPUT: {data_csv}

OUTPUT FORMAT:
### 5 Star Rating
- Summary of all five star ratings as 4-5 points. No separate subheading required.
- Tags: "Tag 1", "Tag 2"

### 4 Star Rating
- Summary of all four star ratings as 4-5 points. No separate subheading required.
- Tags: "Tag 1", "Tag 2"

### 3 Star Rating
- Summary of all three star ratings as 4-5 points. No separate subheading required.
- Tags: "Tag 1", "Tag 2"

### 2 Star Rating
- Summary of all two star ratings as 4-5 points. No separate subheading required.
- Tags: "Tag 1", "Tag 2"

### 1 Star Rating
- Summary of all one star ratings as 4-5 points. No separate subheading required.
- Tags: "Tag 1", "Tag 2"
"""
    messages = [
                    SystemMessage(content = "You are a content analyser for products."),
                    HumanMessage(content = prompt)
                ]
                
    response = llm(messages)
    result = response.content
    return result

def get_download_link(file_path, file_name):
    with open(file_path, "rb") as f:
        csv_data = f.read()
    b64 = base64.b64encode(csv_data).decode()

    href = f'<a href="data:text/csv;base64,{b64}" download="{file_name}">{file_name}</a>'
    return href
  
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
    p1 = "Samsung Galaxy Z Flip 6"
    p2 = "Dyson V8 Advanced Cordless Vacuum Cleaner"
    p3 = "Other Product"
    user_query = st.selectbox("Select an option:", (p1, p2, p3))
    # Button to trigger the research
    if user_query == p3:
        user_query = st.text_input("Enter product name:")
        
    if st.button("Get Research Report"):
        if user_query:
            with st.spinner("Processing your request..."):
                # Run the async function to get the report
                query = f"""
Generate all content under each heading marked in '##'.
## Sentiment Analysis and Market Insights Report for {user_query}

Conduct a structured sentiment analysis and market insights report for {user_query}:
Consider additional websites like Amazon India, Flipkart, Myntra, Snapdeal, etc as well while generating market insights.

### Overview:
Summarize the product's key features, specifications, and qualities in a professional and concise manner. Include atleast 3 key features in the overview within the summary and make sure to mark the key features and specifications in bold.

### 1. Key Features & Specifications
Provide key features and the specifications for {user_query} as bullet points,it should be precise and to the point.

### 2. Key Pain Points & Issues (Negative Sentiment)
Provide a list of top 3 key pain points and issues with a small description for each, as A, B, C list format. Include a **direct link** to the relevant discussion post so users can access it for further details.
       A. 
       B. 
       C. 
    
### 3. Positive Feedback & Strengths (Positive Sentiment)
Provide a list of top 3 positive feedback and strengths with a small description for each, as A, B, C list format. Include a **direct link** to the relevant discussion post so users can access it for further details.
       A. 
       B. 
       C. 
    
### 4. Feature Requests & User Expectations
    
### 5. Market Trends & Regional Performance
       Format the output as a table with the following columns:
       Region | Sales Performance | Key Strengths | Challenges
    
### 6. Actionable Recommendations (For Brand Strategy & Optimization)

       A. 
       B. 
       C. 
    
### 7. Key Insights for Brand Analysis
       - Product Strengths to Leverage
       - Pain Points to Address
       - Market-Specific Strategy
       
### 8. Comparison Table Across E-Commerce Platforms:
Create a table comparing the product across different websites. Only include websites that have information about the product. The table should include the following columns:
| Website | Product Name | Price | Discount | User Rating | Number of Reviews | Shipping Options | Stock Availability | Return Policy | Seller Name/Verified | Additional Perks |
Websites to consider: Amazon India, Flipkart, Myntra, Snapdeal, Tata CLiQ, AJIO, Paytm Mall, JioMart, Meesho, and IndiaMART.

    
    Provide a final takeaway with the most critical strategic direction.
    
    Overall Sentiment Summary: 
    Add *The Overall Sentiment Summary reflects customer opinions on key product aspects, showing the percentage of positive, negative, and neutral mentions.* line
     Format the following output in % as a table with the following:
    Columns:   Positive Mentions | Negative Mentions | Neutral Mentions
    Rows:   Design & Build Quality | Display & Camera | Battery Performance | Software & Performance | Pricing & Value | Availability & Supply

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

At the end of the report, provide a section with **all individual sources** compiled in a list of clickable links for user reference. Make sure the refrences from both the reports are included.  
"""
                report_type = "research_report"
                report, context, sources = asyncio.run(get_report(query, report_type))
 
                # Display the results
                st.write(report)
            if user_query == p1 or user_query == p2:    
                if not st.session_state.path or st.session_state.product != user_query:
                    with st.spinner("Fetching all user reviews..."):
                        if user_query == p1:
                            path = samsung()
                            url = "https://www.currys.co.uk/products/samsung-galaxy-z-flip6-512-gb-yellow-10266667.html"
                        elif user_query == p2:
                            path = dyson()
                            url = "https://www.currys.co.uk/products/dyson-v8-absolute-cordless-vacuum-cleaner-silver-yellow-10256214.html?searchTerm=dyson%20"
                            
                        st.session_state.path = path
                        st.session_state.product = user_query
                        
                        result = analyze_data(path)
                        st.session_state.analysis_result = result
                st.write("## User Reviews:")
                if url:
                    st.write("### Source:")
                    st.link_button("Visit Website", url)
                st.markdown(st.session_state.analysis_result)
                download_link = get_download_link(st.session_state.path, f"Reviews_{st.session_state.product}.csv")
                st.markdown(download_link, unsafe_allow_html=True)
 
        else:
            st.error("Please enter a valid query.")
 
if __name__ == "__main__":
    main()

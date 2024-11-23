import json
import serpapi
import kaggle
import streamlit as st
from serpapi import GoogleSearch

SERPAPI_API_KEY = "0574cd7956f57a811f46bfdf3beb95a8b097359c0609b3513f1254a9d6a441f4"

USE_CASES_FILE = 'use_cases.json'
INSIGHTS_FILE = 'insights.json'

class ResearchAgent:
    def __init__(self):
        self.use_cases = self.load_json(USE_CASES_FILE)
        self.insights = self.load_json(INSIGHTS_FILE)

    def load_json(self, file_name):
        """Load JSON data from a file."""
        try:
            with open(file_name, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_json(self, file_name, data):
        """Save JSON data to a file."""
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)

    def generate_use_case(self, processed_results):
        """Generate use cases based on the processed insights."""
        use_cases = []

        for result in processed_results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            link = result.get('link', '')

            use_case = {
                "problem": f"Identified opportunity for AI in {title}.",
                "solution": "Develop AI/GenAI solutions tailored to address challenges mentioned in the article.",
                "benefits": "Improves efficiency, customer satisfaction, and operational scalability.",
                "reference": link
            }

            use_case_query = title
            datasets = self.search_kaggle_datasets(use_case_query)
            use_case["datasets"] = datasets

            use_cases.append(use_case)

        self.use_cases.extend(use_cases)
        self.save_json(USE_CASES_FILE, self.use_cases)

    def generate_insights(self, query):
        """Generate insights using SerpAPI."""
        search_params = {
            "q": query,
            "api_key": SERPAPI_API_KEY
        }

        try:
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            if results and results.get("organic_results"):
                insights = []
                for result in results["organic_results"]:
                    insights.append({
                        "title": result.get("title", "No title available"),
                        "snippet": result.get("snippet", "No snippet available"),
                        "link": result.get("link", "No link available")
                    })
                
                self.insights.append({"query": query, "insights": insights})
                self.save_json(INSIGHTS_FILE, self.insights)
                return insights
            else:
                return [{"title": "No results found", "snippet": "Try using a different query.", "link": ""}]
        except Exception as e:
            print(f"Error fetching insights: {e}")
            return [{"title": "Error", "snippet": str(e), "link": ""}]

    def search_kaggle_datasets(self, query):
        """Search for Kaggle datasets based on a query."""
        try:
            datasets = kaggle.api.dataset_list(search=query)
            dataset_links = []
            for dataset in datasets:
                dataset_links.append({
                    "title": dataset.title,
                    "url": f"https://www.kaggle.com/datasets/{dataset.ref}",
                    "description": dataset.description[:200]  
                })
            return dataset_links
        except Exception as e:
            print(f"Error fetching Kaggle datasets: {e}")
            return []

agent = ResearchAgent()

def app():
    st.title("AI Use Case Generation & Dataset Fetching")

    query = st.text_input("Enter a query or industry term (e.g., AI in Healthcare):")

    if st.button("Generate Insights and Use Cases"):
        if query:
            insights = agent.generate_insights(query)
            
            st.subheader("Generated Insights:")
            for insight in insights:
                st.write(f"**Title**: {insight['title']}")
                st.write(f"**Snippet**: {insight['snippet']}")
                st.write(f"**Link**: {insight['link']}")

            if insights and insights[0]["title"] != "No results found":
                processed_results = [{"title": query, "snippet": str(insights), "link": insights[0].get("link", "")}]
                agent.generate_use_case(processed_results)
                
                st.subheader("Generated Use Cases:")
                for idx, use_case in enumerate(agent.use_cases, 1):
                    st.write(f"{idx}. **Problem**: {use_case['problem']}")
                    st.write(f"   **Solution**: {use_case['solution']}")
                    st.write(f"   **Benefits**: {use_case['benefits']}")
                    st.write(f"   **Reference**: {use_case['reference']}")
                    st.write(f"   **Datasets**: {', '.join([dataset['title'] for dataset in use_case['datasets']])}")

                st.success("Insights and use cases generated successfully!")
            else:
                st.warning("No valid insights found to generate use cases.")

        else:
            st.error("Please enter a query to generate insights.")

    if st.button("View Saved Use Cases"):
        st.subheader("Saved Use Cases:")
        for idx, use_case in enumerate(agent.use_cases, 1):
            st.write(f"{idx}. **Problem**: {use_case['problem']}")
            st.write(f"   **Solution**: {use_case['solution']}")
            st.write(f"   **Benefits**: {use_case['benefits']}")
            st.write(f"   **Datasets**: {', '.join([dataset['title'] for dataset in use_case['datasets']])}")

    if st.button("View Saved Insights"):
        st.subheader("Saved Insights:")
        for idx, insight in enumerate(agent.insights, 1):
            query = insight.get('query', 'Unknown Query')  
            st.write(f"{idx}. **Query**: {query}")

            st.write(f"   **Insights**: ")
            for res in insight['insights']:
                st.write(f"     - {res['title']} | {res['snippet']} | {res['link']}")

if __name__ == "__main__":
    app()

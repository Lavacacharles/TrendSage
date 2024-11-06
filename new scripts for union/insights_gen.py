import openai 
import pandas as pd
import re
from typing import Optional, List, Dict, Union
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

class InsightAnalyzer:
    """
    A class to analyze and generate insights from social media data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer with OpenAI API key"""
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.setup_logging()

    def setup_logging(self):
        """Configure logging settings"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _make_openai_request(self, system_content: str, user_content: str) -> str:
        """Make a request to OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            return f"Error: {str(e)}"

    def get_description_recommendation(self, df: pd.DataFrame, min_views: int) -> str:
        """Generate recommended description based on successful posts"""
        df_filtered = df[df["playCount"] > min_views]
        text = " ".join(df_filtered["text"].astype(str).values)
        
        return self._make_openai_request(
            "you are in charge of the marketing sector",
            f"Below you have all the descriptions of videos that have a number of views greater than {min_views}, which is the following {text}. I want you to analyze everything and return me the ideal description to create a high-impact video that produces great number of views. (Give me the description in Spanish please)(It is a description of tiktok, it should not be large in size)The characters should not exceed 50-100 [just give me the description, don't give me any more extra]"
        )

    def get_main_ideas(self, df: pd.DataFrame, min_views: int, num_ideas: int) -> List[str]:
        """Extract main ideas from successful posts"""
        df_filtered = df[df["playCount"] > min_views]
        text = " ".join(df_filtered["text"].astype(str).values)
        
        response = self._make_openai_request(
            "you are in charge of the marketing sector",
            f"Below you have all the descriptions of videos that have a number of views greater than {min_views}, which is the following {text}, I want you to analyze these descriptions and tell me what are the {num_ideas} main ideas that the videos have(Give me the description in Spanish please)[I want you to put it in this format ['idea1','idea2', etc]]"
        )
        return eval(response)

    def get_recommended_hashtags(self, df: pd.DataFrame, min_views: int, num_hashtags: int) -> List[str]:
        """Generate recommended hashtags based on successful posts"""
        df_filtered = df[df["playCount"] > min_views]
        hashtags = "|".join(df_filtered["hashtags"].astype(str).values)
        views = "|".join(df_filtered["playCount"].astype(str).values)
        
        response = self._make_openai_request(
            "You are a hashtag analysis assistant.",
            f"Provide only a list of the top {num_hashtags} most impactful hashtags based on this data: views {views} and hashtags {hashtags} [hashtags per video are separated by '|']. Output only in this format: ['hashtag1', 'hashtag2', ...]"
        )
        return eval(response)

    def generate_video_script(self, df: pd.DataFrame, topic: str) -> str:
        """Generate a video script idea based on a specific topic"""
        text = "|".join(df["contenido_limpio"].astype(str).values)
        
        return self._make_openai_request(
            "you are in charge of the marketing sector",
            f"Below you have all the transcripts of the videos that have a good number of views, these are the transcripts of the video {text} [they are separated by the transcripts from each other with '|'], I want you to analyze the descriptions and give me a script idea for a future TikTok video that I want to make that is a little related to this topic {topic}(Give me the description in Spanish please)"
        )

    def get_content_summary(self, df: pd.DataFrame) -> str:
        """Generate a summary of all content"""
        text = "|".join(df["contenido_limpio"].astype(str).values)
        
        return self._make_openai_request(
            "you are in charge of the marketing sector",
            f"Below you have all the transcripts of the videos that have a good number of views, these are the transcripts of the video {text} [they are separated by the transcripts from each other with '|'], I want you to analyze the transcripts and give me a general summary of the videos(Give me the description in Spanish please)[in paragraph format]"
        )

    def get_custom_insight(self, df: pd.DataFrame, query: str) -> Dict[str, Union[str, int]]:
        """Generate custom insights based on specific query"""
        try:
            # First get recommended columns
            columns = list(df.columns)
            columns_response = self._make_openai_request(
                "You are a data analysis assistant.",
                f"Here are the columns: {columns}. Please suggest the best columns for this request: '{query}'. Only return them as a Python list in this format: ['column1', 'column2', ...]. No additional explanation."
            )
            recommended_columns = eval(columns_response)
            
            # Filter existing columns
            existing_cols = [col for col in recommended_columns if col in df.columns]
            if not existing_cols:
                return {
                    "analysis": "Error: No relevant columns found",
                    "num_columns": 0,
                    "num_rows": 0
                }

            # Get insights based on filtered data
            df_filtered = df[existing_cols]
            info_columns = df_filtered.to_string(index=False)
            
            analysis = self._make_openai_request(
                "You are a data analysis assistant.",
                f"Here is data for the relevant columns for this request: '{query}'.\n\n{info_columns}\n\nPlease provide an analysis or insights based on this data.(Give me the description in Spanish please)"
            )
            
            return {
                "analysis": analysis,
                "num_columns": len(existing_cols),
                "num_rows": len(df_filtered)
            }
            
        except Exception as e:
            self.logger.error(f"Error in custom insight: {str(e)}")
            return {
                "analysis": f"Error: {str(e)}",
                "num_columns": 0,
                "num_rows": 0
            }

def main():
    # Example usage
    analyzer = InsightAnalyzer()
    
    # Load your data
    df1 = pd.read_csv("processed_data.csv")
    df2 = pd.read_csv("processed_data2.csv")
    
    # Get various insights
    description = analyzer.get_description_recommendation(df1, 10000)
    main_ideas = analyzer.get_main_ideas(df1, 10000, 3)
    hashtags = analyzer.get_recommended_hashtags(df1, 10000, 3)
    script = analyzer.generate_video_script(df2, "cupcakes de navidad")
    summary = analyzer.get_content_summary(df2)
    custom_insight = analyzer.get_custom_insight(df1, "quiero que me digas que topicos puedo hacer para mis futuros videos")
    
    # Print results
    print("Description:", description)
    print("\nMain Ideas:", main_ideas)
    print("\nHashtags:", hashtags)
    print("\nScript:", script)
    print("\nSummary:", summary)
    print("\nCustom Insight:", custom_insight)

if __name__ == "__main__":
    main()
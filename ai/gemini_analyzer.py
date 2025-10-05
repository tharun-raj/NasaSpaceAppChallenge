from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import os   
from typing import Optional, List, Dict, Any

class MarsImageAnalyzer:

    load_dotenv()
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    async def analyze_mars_tile(self, image_data: bytes, question: str,tile_info: Optional[Dict[str, Any]] = None) -> str:
        try:
            img = Image.open(BytesIO(image_data))
            
            context = ""
            if tile_info:
                z, x, y = tile_info.get('z'), tile_info.get('x'), tile_info.get('y')
                dataset = tile_info.get('dataset', 'global')
                context = f"\n\nContext: This is a Mars surface tile from the {dataset} dataset at zoom level {z}, tile coordinates ({x}, {y})."
            
            prompt = f"""You are analyzing a Mars surface image. Please answer the following question with detailed, scientific observations.
                Question: {question}{context}
                Provide a thorough analysis including:
                - Direct answer to the question
                - Observable surface features (craters, rocks, terrain patterns)
                - Geological characteristics
                - Any notable formations or anomalies
                - Scale and context of visible features
                Be specific, accurate, and scientific in your response."""

            response = self.model.generate_content([prompt, img])
            return response.text
        
        except Exception as e:
            raise Exception(f"Failed to analyze image: {str(e)}")
    
    async def analyze_general_features(self, image_data: bytes) -> str:
        try:
            img = Image.open(BytesIO(image_data))
            
            prompt = """Analyze this Mars surface image and provide a comprehensive description:

                1. **Terrain Type**: Identify the type of terrain (plains, highlands, crater field, etc.)
                2. **Surface Features**: List all visible geological features
                3. **Craters**: Describe any impact craters (size, distribution, preservation state)
                4. **Rocks and Boulders**: Note any visible rocks or boulder fields
                5. **Color and Texture**: Describe surface coloration and texture patterns
                6. **Geological Processes**: Identify signs of erosion, deposition, or other processes
                7. **Notable Observations**: Any interesting or unusual features

                Be detailed and scientific in your analysis."""

            response = self.model.generate_content([prompt, img])
            return response.text
        
        except Exception as e:
            raise Exception(f"Failed to analyze features: {str(e)}")
    
    async def detect_specific_features(self, image_data: bytes, features: List[str]) -> str:
        try:
            img = Image.open(BytesIO(image_data))
            
            features_str = ", ".join(features)
            prompt = f"""Examine this Mars surface image and detect the following features: {features_str}

                For each requested feature:
                1. Presence: Is it visible in this image? (Yes/No/Possibly)
                2. Location: Where in the image? (e.g., center, top-left, scattered)
                3. Characteristics: Describe its appearance, size, and condition
                4. Count/Distribution: If multiple, how many and how are they distributed?
                5. Additional Notes: Any interesting observations

                Be precise and thorough in your detection."""

            response = self.model.generate_content([prompt, img])
            return response.text
        
        except Exception as e:
            raise Exception(f"Failed to detect features: {str(e)}")
    
    async def compare_tiles(self, image1_data: bytes, image2_data: bytes,tile1_info: Optional[Dict] = None,tile2_info: Optional[Dict] = None) -> str:
        try:
            img1 = Image.open(BytesIO(image1_data))
            img2 = Image.open(BytesIO(image2_data))
            
            context = ""
            if tile1_info and tile2_info:
                context = f"""
                    Tile 1: {tile1_info.get('dataset')} dataset, zoom {tile1_info.get('z')}, coordinates ({tile1_info.get('x')}, {tile1_info.get('y')})
                    Tile 2: {tile2_info.get('dataset')} dataset, zoom {tile2_info.get('z')}, coordinates ({tile2_info.get('x')}, {tile2_info.get('y')})
                    """
            
            prompt = f"""Compare these two Mars surface images and identify:
                {context}
                1. **Similarities**: Common features, terrain types, or patterns
                2. **Differences**: Distinct characteristics between the images
                3. **Terrain Variation**: How does the landscape differ?
                4. **Geological Features**: Different or similar geological structures
                5. **Surface Conditions**: Variations in surface texture, color, or composition
                6. **Scale Differences**: If at different zoom levels, describe what changes
                Provide a detailed comparative analysis."""

            response = self.model.generate_content([
                prompt, 
                "First Mars tile:", img1, 
                "Second Mars tile:", img2
            ])
            return response.text
        
        except Exception as e:
            raise Exception(f"Failed to compare images: {str(e)}")
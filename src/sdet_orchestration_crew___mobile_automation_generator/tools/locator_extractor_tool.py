import os
import json
import time
import concurrent.futures
from collections import defaultdict
from google import genai
from google.genai import types
from crewai.tools import BaseTool
from pydantic import BaseModel

class LocatorExtractionToolInput(BaseModel):
    """Empty input schema because the tool auto-scans the directory."""
    pass

class LocatorExtractionTool(BaseTool):
    name: str = "Autonomous Locator Extraction Tool"
    description: str = (
        "Automatically scans the 'assets/screens' directory, groups screenshots with their XML dumps, "
        "and extracts locators for all UI elements in parallel. "
        "Call this tool WITHOUT any arguments."
    )
    args_schema: type[BaseModel] = LocatorExtractionToolInput

    def _group_assets(self, base_dir: str) -> dict:
        """Groups files in the assets/screens directory using Python string matching."""
        groups = defaultdict(lambda: {"image": None, "android": None, "ios": None})
        if not os.path.exists(base_dir):
            return groups

        for f in os.listdir(base_dir):
            if f.startswith('.'): continue # Skip hidden files
            
            lower_f = f.lower()
            if lower_f.endswith(('.png', '.jpg', '.jpeg')):
                base_name = os.path.splitext(f)[0]
                groups[base_name]['image'] = f
            elif lower_f.endswith('.xml'):
                if '_android' in lower_f:
                    base_name = lower_f.replace('_android.xml', '')
                    groups[base_name]['android'] = f
                elif '_ios' in lower_f:
                    base_name = lower_f.replace('_ios.xml', '')
                    groups[base_name]['ios'] = f
                else:
                    # Default to Android if no platform suffix is found
                    base_name = os.path.splitext(f)[0]
                    groups[base_name]['android'] = f
        return groups

    def _analyze_single_screen(self, screen_name: str, files: dict, client: genai.Client, base_dir: str) -> dict:
        print(f"  -> Processing screen: {screen_name}")
        
        # 1. Safely read XMLs
        android_xml = "No Android XML provided."
        if files['android']:
            with open(os.path.join(base_dir, files['android']), 'r', encoding='utf-8') as f: 
                android_xml = f.read()
                
        ios_xml = "No iOS XML provided."
        if files['ios']:
            with open(os.path.join(base_dir, files['ios']), 'r', encoding='utf-8') as f: 
                ios_xml = f.read()

        # 2. Upload image
        if not files['image']:
            return {screen_name: {"error": "No screenshot found for this screen."}}
            
        try:
            img_path = os.path.join(base_dir, files['image'])
            uploaded_file = client.files.upload(file=img_path)
        except Exception as e:
            return {screen_name: {"error": f"Upload failed: {str(e)}"}}

        # 3. Construct prompt
        prompt = f"""
        Analyze the screenshot and XML dumps for the UI state: '{screen_name}'.
        Identify the interactive elements (buttons, inputs, text, toasts).
        
        Return ONLY a raw JSON dictionary where the keys are logical element names, and values are locator dictionaries.
        Android preference: resource-id, content-desc, xpath.
        iOS preference: accessibility-id, name, predicate-string, class-chain, xpath.
        
        Android XML:
        ```xml
        {android_xml}
        ```
        
        iOS XML:
        ```xml
        {ios_xml}
        ```

        Format Example:
        {{
            "username_input": {{ "android": ["id", "com.app:id/username"], "ios": ["accessibility id", "username_field"] }},
            "error_toast": {{ "android": ["xpath", "//*[@text='Invalid Credentials']"], "ios": ["accessibility id", "error_message"] }}
        }}
        
        Return ONLY valid JSON. Do not include markdown formatting blocks like ```json.
        """

        # 4. Call Gemini using the NEW SDK
        try:
            # Stagger requests slightly to avoid hitting the 15 RPM Free Tier limit too hard
            time.sleep(2) 
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, uploaded_file],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1 # Low temperature for more deterministic locators
                )
            )
            return {screen_name: json.loads(response.text.strip())}
        except Exception as e:
            return {screen_name: {"error": f"Generation failed: {str(e)}"}}

    def _run(self) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: return "Error: GEMINI_API_KEY not set."
        
        # Initialize the new SDK client
        client = genai.Client(api_key=api_key)
        base_dir = os.path.join(os.getcwd(), "assets/screens")
        
        # Group the files using our Python logic
        grouped_assets = self._group_assets(base_dir)
        print(f"\n[Batch Tool] Found {len(grouped_assets)} logical screens. Starting parallel analysis...")

        master_locator_dict = {}
        
        # Execute parallel calls (max_workers=3 is safe for Free Tier 15 RPM limits)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self._analyze_single_screen, name, files, client, base_dir)
                for name, files in grouped_assets.items()
            ]
            for future in concurrent.futures.as_completed(futures):
                try:
                    master_locator_dict.update(future.result())
                except Exception as exc:
                    print(f"  -> Thread generated an exception: {exc}")

        return json.dumps(master_locator_dict, indent=2)
import streamlit as st
import io
from PIL import Image
import requests
import base64
from models import gemini_generate, openrouter_generate, vlm_generate
# from pybooru import Danbooru
from gelbooru import search_anime_character

# https://pypi.org/project/aiodanbooru/
# pip install aiodanbooru

def vlm_prompt(webcam_image, downloaded_image):
    ### ret a prompt of how to merge the webcam image and downloaded image
    webcam_bytes = webcam_image.getvalue()
    webcam_b64 = base64.b64encode(webcam_bytes).decode('utf-8')

    # Convert PIL image to bytes then base64
    img_buffer = io.BytesIO()
    downloaded_image.save(img_buffer, format='PNG')
    anime_b64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    analysis_prompt = """Analyze these two images carefully:
1. The first image shows a real person
2. The second image shows an anime character
You are not expected to generate an image, but to create a prompt instead.
Create a detailed transformation prompt for converting the real person into anime style. Be specific about:

PHYSICAL FEATURES TO PRESERVE:
- Age and gender of the person
- Basic facial structure and proportions
- Hair length and style
- Pose and expression
- Background elements

ANIME STYLE TO ADOPT:
- Art style from the anime reference (cel-shaded, soft-shaded, etc.)
- Color palette and vibrancy
- Eye style and size
- Line art thickness
- Shading technique

Format as a clear, actionable prompt for image generation. Start with "Transform this person into anime style:" and include specific technical terms like "cel-shaded", "anime proportions", "vibrant colors", etc.

Make it practical for AI image generation."""

    analysis = vlm_generate(webcam_b64, anime_b64, analysis_prompt)

    # Create a more structured final prompt
    final_prompt = f"""Given these two reference images, {analysis}

Technical requirements:
- Maintain the original person's pose, facial structure, and background
- Apply anime art style with cell-shading and bold outlines
- Use vibrant anime color palette
- Transform facial features to anime proportions while keeping recognizable identity
- High quality anime artwork style"""

    return final_prompt

def search_agent(prompt):
    ### ret b64 image of downloaded anime character from prompt

    # 1. use ai to parse prompt into proper anime character name.
    # 2. if unable to find name, traits such as hair, eye color, height are also acceptable
    prompt = f"""Parse this anime character description and extract search terms for booru image boards: "{prompt}"

    IMPORTANT: Use only valid booru tags in this format:
    - Character names: lowercase, underscores for spaces (e.g., "megumin", "gojo", "gojo_satoru")
    - Series names: with underscores (e.g., "konosuba", "jujutsu_kaisen")
    - Physical traits: standardized tags (e.g., "red_eyes", "brown_hair", "long_hair")
    - Always include "1girl" or "1boy" as appropriate
    - Use tags like "official_art" or "anime_screenshot" for better quality

    Examples:
    - "megumin konosuba red_eyes brown_hair 1girl official_art"
    - "gojo_satoru jujutsu_kaisen white_hair blue_eyes 1boy"
    - "zero_two darling_in_the_franxx pink_hair red_horns 1girl"

    Return only the search tags separated by spaces, no explanations."""
    search_query = openrouter_generate(prompt)

    # https://openrouter.ai/docs/features/tool-calling
    # 3. use https://www.animecharactersdatabase.com or danbooru
    try:
        # tag_list = '_'.join(search_query.strip().split()[:2]) if search_query else "1girl"
        # posts = danbooru.post_list(tags="1girl", limit=1, page=1, random=True)
        # print(posts[0])
        # if posts[0].get('file_url'):
        #     file_url = posts[0]['file_url']
        # elif posts[0].get('large_file_url'):
        #     file_url = posts[0]['large_file_url']
        # else:
        #     # Fallback to sample if no high-res available
        #     file_url = posts[0]['media_asset']['variants'][-1]['url']

        # Download the image and convert to base64
        file_url = search_anime_character(search_query)
        if not file_url:
            file_url = search_anime_character("1girl")

        if file_url:
            response = requests.get(file_url)
            response.raise_for_status()
            image_b64 = base64.b64encode(response.content).decode('utf-8')
            return image_b64
        else:
            raise Exception("Could not find any anime character image")
    except Exception as e:
       print(f"Search failed: {e}")
       # Return None to indicate failure
       return None

# def generate_image(original_img: bytes, prompt: str):
def generate_image(original_img: bytes, anime_img: bytes, prompt: str):
    ### ret image in bytes for st.image() and bytesio
    b64 = base64.b64encode(original_img).decode('utf-8')
    b64_2 = base64.b64encode(anime_img).decode('utf-8')
    gemini_bytes = gemini_generate(b64, b64_2, prompt)
    # openai_bytes = openai_generate(b64, prompt)
    if gemini_bytes is None:
        print("Error: gemini_generate returned None")
        return None
    return gemini_bytes

# Streamlit UI
st.title("Anime Transformation Studio")

# Input Section
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Take Your Photo")
    enable = st.checkbox("Enable camera")
    user_img = st.camera_input("Take a picture", disabled=not enable)

with col2:
    st.subheader("2. Choose Anime Character")
    char_prompt = st.text_input("Character prompt (e.g. 'Megumi Jujutsu Kaisen')")

if user_img and char_prompt:
    with st.status("Processing..."):
        # Pre-process images
        st.write("Processing images...")

        st.write("Searching character reference...")
        anime_b64 = search_agent(char_prompt)
        if anime_b64 is None:
            st.error("Failed to find anime character reference. Please try a different character name.")
            st.stop()
        anime_image = Image.open(io.BytesIO(base64.b64decode(anime_b64)))

        # Display references
        st.subheader("Input References")
        ref_col1, ref_col2 = st.columns(2)
        with ref_col1:
            st.image(user_img, caption="Your Photo")
        with ref_col2:
            st.image(anime_image, caption="Anime Reference")

        # Generate prompt
        st.write("Generating fusion prompt...")
        final_prompt = vlm_prompt(user_img, anime_image)
        st.subheader("Generated Transformation Prompt")
        st.write(final_prompt)

        # Generate final image
        st.write("Creating artwork...")
        generated_bytes = generate_image(user_img.getvalue(), base64.b64decode(anime_b64), final_prompt)

        if generated_bytes is None:
            st.error("Failed to generate image. Please try again with a different character or photo.")
            st.stop()

        final_image = Image.open(io.BytesIO(generated_bytes))

    # Display result
    st.subheader("Your Anime Transformation")
    st.image(final_image)

    # Download button
    img_bytes = io.BytesIO()
    final_image.save(img_bytes, format="PNG")
    st.download_button(
        label="Download Postcard",
        data=img_bytes.getvalue(),
        file_name="output/anime_transformation.png",
        mime="image/png"
    )

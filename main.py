import streamlit as st
import io
from PIL import Image
import requests
import base64
import urllib.parse
from models import gemini_generate, openai_generate, openrouter_generate, vlm_generate
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

    analysis_prompt = """Analyze these two images:
1. The first image shows a real person
2. The second image shows an anime character

Create a detailed art generation prompt that describes how to transform the real person into the anime character's style. Include:
- Physical features from the real person (hair color, face shape, age, etc.)
- Art style elements from the anime character (shading style, color palette, aesthetic)
- Specific anime art techniques like "cell-shaded", "bold outlines", "vibrant colors"

Format your response as a single detailed prompt suitable for an AI art generator.

Example format: "[age] [gender] with [physical features] in [character name]'s [art style], [pose description], anime cell-shaded style, detailed eyes, [series] aesthetic"
"""

    analysis = vlm_generate(webcam_b64, anime_b64, f"{analysis_prompt}")

    # Combine both analyses into a final prompt
    final_prompt = f"""Transform the real person into anime style based on these analyses:

{analysis}


Create a fusion that maintains the person's identity while adopting the anime character's art style, including cell-shading, vibrant colors, and anime aesthetic."""

    return final_prompt

def search_agent(prompt):
    ### ret b64 image of downloaded anime character from prompt

    # 1. use ai to parse prompt into proper anime character name.
    # 2. if unable to find name, traits such as hair, eye color, height are also acceptable
    prompt = f"""Parse this anime character description and extract the most important search terms for finding an image of this character: "{prompt}"

    Extract:
    1. Character name (if mentioned)
    2. Anime/series name (if mentioned)
    3. Key visual traits (hair color, eye color, clothing, etc.)

    Format your response as a simple search query that would work well for finding images of this character on anime character databases. Focus on the most distinctive features.
    Focus on using booru image board tags.

    Example: "Megumin red eyes choker blush brown_hair thighhighs 1girl dress"

    Just return the search terms, nothing else."""
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
            response = requests.get(file_url)
            response.raise_for_status()
            image_b64 = base64.b64encode(response.content).decode('utf-8')

        if file_url:
            response = requests.get(file_url)
            response.raise_for_status()
            image_b64 = base64.b64encode(response.content).decode('utf-8')
        return image_b64
    except Exception as e:
       print(f"Search failed: {e}")
       # Return a simple placeholder image as base64
       return "meow"

def generate_image(original_img: bytes, prompt: str):
    ### ret image in bytes for st.image() and bytesio
    b64 = base64.b64encode(original_img).decode('utf-8')
    gemini_bytes = gemini_generate(b64, prompt)
    # openai_bytes = openai_generate(b64, prompt)
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
        st.subheader("Final prompt")
        st.write(final_prompt)
        # Generate final image
        st.write("Creating artwork...")
        final_image = generate_image(user_img.getvalue(), final_prompt)
        final_image = Image.open(io.BytesIO(final_image))

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

# gemini for vision / image generation possibly
# gpt-image-1 api for image generation possibly
# free openrouter vlm for recognising / prompting
# openrouter free small llm for tool calling / searching for image and downloading

from google import genai
from google.genai import types
import base64
import mimetypes
import os
from openai import OpenAI

if os.environ.get("GOOGLE_API_KEY") == "":
    print("no gemini api key wtf ur COOKED")

gemini_client = genai.Client(
    api_key="meow" if os.environ.get("GOOGLE_API_KEY") == "" else (os.environ.get("GOOGLE_API_KEY") or "meow"),
)

openai_client = OpenAI()

openrouter_client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="meow" if os.environ.get("OPENROUTER_API_KEY") == "" else (os.environ.get("OPENROUTER_API_KEY") or "meow"),
)

def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def gemini_generate(b64_image: str, b64_image_2: str, input: str):
    # taken from google ai studio
    model = "gemini-2.0-flash-preview-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                *(
                    [types.Part.from_bytes(
                        mime_type="image/png",
                        data=base64.b64decode(b64_image)
                    )] if b64_image else []
                ),
                *(
                    [types.Part.from_bytes(
                        mime_type="image/png",
                        data=base64.b64decode(b64_image_2)
                    )] if b64_image_2 else []
                ),
                types.Part.from_text(text=input),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT"
        ],
        response_mime_type="text/plain",
    )

    file_index = 0
    for chunk in gemini_client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"ENTER_FILE_NAME_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data # image bytes
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            os.makedirs("output", exist_ok=True)
            save_binary_file(f"output/{file_name}{file_extension}", data_buffer)
            return data_buffer
        else:
            print(chunk.text)

def openai_generate(b64_image: str, input: str):
    # https://platform.openai.com/docs/guides/image-generation?image-generation-model=gpt-image-1&api=responses#edit-images
    response = openai_client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
            "role": "user",
            "content": [
                {"type": "input_text", "text": input},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{image}",
                }
            ],
            }
        ],
        tools=[{"type": "image_generation"}],
    )
    image_generation_calls = [
        output
        for output in response.output
        if output.type == "image_generation_call"
    ]

    image_data = [output.result for output in image_generation_calls]

    if image_data:
        image_base64 = image_data[0]
        return image_base64
    else:
        print(response.output.content)

def vlm_generate(webcam_image: str, downloaded_image: str, prompt: str):
    completion = openrouter_client.chat.completions.create(
        model="google/gemma-3-27b-it:free",
        # model="qwen/qwen2.5-vl-32b-instruct:free",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{webcam_image}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{downloaded_image}"
                        }
                    }
                ]
            }
        ]
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def openrouter_generate(prompt: str):
    completion = openrouter_client.chat.completions.create(
        extra_body={},
        model="deepseek/deepseek-r1-0528-qwen3-8b:free",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                ]
            }
        ]
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

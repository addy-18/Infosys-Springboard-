
import os
import google.generativeai as genai
import sounddevice as sd
import wavio
import openpyxl
from datetime import datetime

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def record_audio(file_name, duration=5, sample_rate=44100):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    wavio.write(file_name, audio, sample_rate, sampwidth=2)
    print(f"Audio saved to {file_name}")


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


def save_to_excel(file_name, analysis):
    excel_file = "analysis_results.xlsx"

    # Checking if an Excel file exists
    if not os.path.exists(excel_file):
        # Create a new Excel workbook
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Analysis Results"
        sheet.append(["Record Name", "Analysis"])
        workbook.save(excel_file)

   
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook.active
    sheet.append([file_name, analysis])
    workbook.save(excel_file)
    print(f"Results saved to {excel_file}")

# Main function
def main():
    #Record a new audio file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    audio_file_name = f"Recorded_Audio_{timestamp}.wav"
    record_audio(audio_file_name, duration=5)

    #Upload the recorded audio to Gemini
    gemini_file = upload_to_gemini(audio_file_name, mime_type="audio/wav")

    #Creating the model for sentiment and tone analysis
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction="You are a sentiment and tone analysis agent. Provide a short summary of both sentiment and tone in one concise sentence.",
    )

    #analysis
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    gemini_file,
                ],
            }
        ]
    )
    response = chat_session.send_message("Analyze the sentiment and tone of this audio.")
    print("Analysis Response:")
    print(response.text)

    #Extracting analysis summary
    analysis = response.text.strip()

    #Saving the results to an Excel file
    save_to_excel(audio_file_name, analysis)

if __name__ == "__main__":
    main()

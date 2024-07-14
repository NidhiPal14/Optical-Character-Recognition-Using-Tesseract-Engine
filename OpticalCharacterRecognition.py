#necessary libraries
import pytesseract
import cv2
from googletrans import Translator, LANGUAGES
import pyttsx3
import tkinter as tk
from tkinter import filedialog
from pdf2image import convert_from_path
import numpy as np

#set tesseract command path
pytesseract.pytesseract.tesseract_cmd = "D:\\Tesseract_f\\tesseract.exe"

#function to open dialog box for prompting  user to upload image 
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select an Image or PDF",
        filetypes=[("Image and PDF Files", "*.png;*.jpg;*.jpeg;*.pdf"),
                   ("Image Files", "*.png;*.jpg;*.jpeg"),
                   ("PDF Files", "*.pdf")]
    )
    return file_path


root = tk.Tk()
root.title("File Selection")
root.geometry("400x200")

file_path = None

#handling pdf file or image selection 
def on_select_file():
    global file_path
    file_path = select_file()
    root.quit()


btn_select_file = tk.Button(root, text="Select Image or PDF from Folder", command=on_select_file)
btn_select_file.pack(pady=10)

root.mainloop()
root.destroy()

if not file_path:
    print("No file selected. Exiting.")
    exit()

is_pdf = file_path.lower().endswith(".pdf")


if is_pdf:
    pages = convert_from_path(file_path, 300)
    images = []
    for page in pages:
        images.append(cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR))
else:
    image = cv2.imread(file_path)
    if image is None:
        print(f"Error: Unable to read the image at {file_path}.")
        exit()
    images = [image]
#applying binary thesholding to images using OTSU'S METHOD for preprocessing images
for image in images:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


    #text extraction using tesseract
    extracted_text = pytesseract.image_to_string(processed_image, lang='deu')

    
    #translation of extracted text
    translator = Translator()
    detected_language = translator.detect(extracted_text).lang
    print("Detected Language:", LANGUAGES.get(detected_language, "Unknown"))
    language = input("Enter the language code (e.g., 'es' for Spanish, 'fr' for French): ").strip()
    translated_text = translator.translate(extracted_text, dest=language).text

    print(f"Extracted Text: {extracted_text}")
    print(f"Translated Text: {translated_text}")


    #speaking aloud extracted text 
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(translated_text)
    engine.runAndWait()

    #drawing bounding boxes and putting detected text over bounding boxes for clear veiw of extracted text in image 
    if not is_pdf:
        results = pytesseract.image_to_data(processed_image)
        #print(results)  run this to see details of data extracted by tesseract from image 
        for ind, line in enumerate(results.splitlines()):
            if ind != 0:
                line = line.split()
                 #print(line) run this to see individual componenets of each line in image details
                if len(line) == 12:
                    x, y, w, h = int(line[6]), int(line[7]), int(line[8]), int(line[9])
                    cv2.rectangle(image, (x, y), (w + x, h + y), (0, 255, 0), 2)
                    cv2.putText(image, line[11], (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
        #display the image with bounding boxes
        cv2.imshow("Input", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

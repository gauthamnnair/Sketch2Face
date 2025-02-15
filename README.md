# 📌 Sketch2Face – Criminal Sketch Recognition System  

## 🔍 Overview  

**Sketch2Face** is an AI-powered **criminal sketch processing and recognition system**.  
It:  
✅ **Reconstructs realistic images** from uploaded sketches using a trained **VAE model**.  
✅ **Compares the reconstructed image** with a database of real photos using **DeepFace**.  
✅ **Finds the most similar face** using a combination of **cosine similarity and Euclidean distance**.  
✅ **Stores logs of uploads & reconstructions** for future reference.  
✅ **Secure login system** to prevent unauthorized access.  

---

## 📂 Project Structure  


Sketch2Face
main.py                # Main application (Tkinter GUI with login, upload, processing)
compare.py             # Compares reconstructed images with a dataset
run_model.py           # Generates reconstructed images from uploaded sketches
Model_Maker.ipynb      # Notebook for training the VAE model
logs/                  # Stores all uploaded & reconstructed images
temp/                  # Temporary directory for uploaded images
Kaggle/photos/         # Dataset of real images for comparison
requirements.txt       # Required Python dependencies

---

## 🚀 Features  

✔ **Secure Login System** – Users must log in before accessing the application.  
✔ **Sketch Upload & Reconstruction** – Converts sketches into realistic images using a **Variational Autoencoder (VAE)**.  
✔ **Face Comparison using Deep Learning** – Uses **DeepFace** for accurate face matching.  
✔ **Similarity Score Calculation** – Uses a **hybrid scoring system** based on **cosine similarity and Euclidean distance**.  
✔ **Log Management** – Saves **each upload & reconstruction** inside a numbered folder for easy tracking.  

---

## ⚙️ Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/yourusername/Sketch2Face.git
cd Sketch2Face
```

###2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

**🔗 Model Download Link:** [Click Here](https://drive.google.com/file/d/1xjaaxZM-LaHU8L5MX9elyxRf0qEM9e_B/view?usp=drive_link)  

###🖥️ How to Run
###🔑 Step 1: Start the Application
```bash
python main.py
```
    Login with credentials:
        Username: admin
        Password: password123

###📤 Step 2: Upload a Sketch

    Click "Upload Sketch", select a file, and confirm.

###🎨 Step 3: Generate & Compare

    Click "Submit Sketch" to generate a realistic face and find the closest match.
    Wait 2-3 minutes for processing.

###📂 Step 4: View Results & Logs

    See three images side-by-side:
    ✅ Original Sketch
    ✅ AI-Reconstructed Image
    ✅ Most Similar Face Match (with similarity score)
    Results are automatically saved inside the logs/ folder.

🛠️ How It Works
1️⃣ Reconstruction with VAE

    The VAE (Variational Autoencoder) model in run_model.py reconstructs realistic faces from sketches.
    Trained using Kaggle's Sketch-to-Real dataset.

2️⃣ Face Comparison with DeepFace

    compare.py extracts facial embeddings from the reconstructed image and real dataset.
    Uses Facenet model to compare features.
    Ranking method:
        Higher Cosine Similarity = More similar
        Lower Euclidean Distance = More similar

3️⃣ Hybrid Similarity Score Calculation
Final Score=(Cosine Similarity×100)−(Euclidean Distance10×100)
Final Score=(Cosine Similarity×100)−(10Euclidean Distance​×100)

    Higher Score = Better Match
    Logs the results in logs/ folder.

📜 Example Output

Using Facenet model for comparison...
Computing embedding for the reconstructed image...
Most similar image: suspect_002.jpg
Cosine Similarity: 0.9421, Euclidean Distance: 2.3874
Final Similarity Score: 85.35

    The most similar face is suspect_002.jpg, and 85.35% accurate.

📸 Example UI Screenshot

✅ Main Interface (Sketch Upload & Processing)

✅ Final Output (3 Images Side by Side)
📌 Notes

    Processing Time: 2-3 mins per image (depends on model & hardware).
    Default Face Matching Model: "Facenet" (Can be changed in compare.py).
    Dataset Location: Kaggle/photos/ (Make sure this folder has real images).

🛠️ Future Improvements

🚀 Train a More Advanced GAN Model for even better reconstructions.
🎯 Improve Face Matching Algorithm for more accurate results.
📡 Deploy as a Web App using Flask or FastAPI.
🔐 Implement Multi-User Authentication for different access levels.
📩 Contact & Contributions

Want to contribute? Pull requests are welcome! 🎉
📧 Email: gauthamnnair@tutanota.com
🌍 GitHub: github.com/gauthamnnair
📜 License

This project is licensed under the MIT License.
🚀 Final Thoughts

Sketch2Face is a powerful AI-based tool that helps reconstruct and match criminal sketches. 🚔🔍
Let’s make forensic investigation smarter and faster! 🚀🎯
✅ Next Steps

1️⃣ Copy & Save This README as README.md.
2️⃣ Update GitHub Links (replace yourusername with your actual GitHub username).
3️⃣ Run & Test Everything – If all works fine, push to GitHub!

Now your project Sketch2Face has a detailed README! 🚀😊
Let me know if you need any more modifications!


# Spotify Album Poster Generator

This project is a Python application that allows you to create customizable album posters by fetching album information from Spotify **or** reading from local files. It comes with a modern and easy-to-use graphical user interface (GUI) built using Streamlit.

## Table of Contents

-   [Features](#features "null")
    
-   [File Structure](#file-structure "null")
    
-   [Installation](#installation "null")
    
-   [Running the Application](#running-the-application "null")
    
-   [Usage](#usage "null")
    
-   [Multi-language Support](#multi-language-support "null")
    
-   [Contributing](#contributing "null")
    
-   [License](#license "null")
    

## Features

-   **Spotify Integration:** Search for albums directly from the Spotify API and fetch their information (album name, artist, tracks, cover art). **Requires Spotify API credentials.**
    
-   **Local File Support:** Load album data from a local JSON file (Spotify API format or similar). You can also upload album cover art from a local image file. **Does NOT require Spotify API credentials.**
    
-   **Customizable Posters:**
    
    -   Create posters in different sizes (A4, A3, A2).
        
    -   Adjust the number of tracks per column for the tracklist.
        
    -   Adjust the horizontal position of the tracklist.
        
    -   Option to include copyright information.
        
-   **Multi-language Support:** Select the language for the application interface. Texts are stored in separate `.lang` files, making it easy to add new languages.
    
-   **Modern GUI:** Interactive and user-friendly interface built with Streamlit.
    

## File Structure

The project has the following file and directory structure:

```
.
├── fonts/              # Contains font files used for poster drawing.
│   ├── bold.otf        # Bold font file.
│   ├── light.otf       # Light font file.
│   ├── medium.otf      # Medium font file.
│   ├── regular.otf     # Regular font file.
│   ├── semibold.otf    # Semi-bold font file.
│   ├── thin.otf        # Thin font file.
│   ├── verybold.otf    # Very bold font file.
│   └── verylight.otf   # Very light font file.
├── gui.py              # Contains the Streamlit GUI interface code. This file is run to start the application.
├── lang/               # Directory containing the application's multi-language text files.
│   ├── eng.lang        # English language strings.
│   └── tr.lang         # Turkish language strings.
├── languages.py        # Python module that loads language strings by reading .lang files in the 'lang' directory.
└── poster_core.py      # Python module containing the core logic for poster creation and drawing. Used by gui.py.
```

## Installation

Follow these steps to run the project on your local machine:

1.  **Clone the Repository:**
    
    ```
    git clone https://github.com/Aykut551/SpotifyPosterMaker.git
    cd SpotifyPosterMaker
    ```
    
    
2.  **Create a Python Virtual Environment (Recommended):**
    
    ```
    
    python -m venv venv
    
    source venv/bin/activate   # Linux/macOS
    
    venv\Scripts\activate    # Windows
    
    ```
    
3.  **Install Dependencies:**
    
    ```
    pip install -r requirements.txt
    ```
    
4.  **Set Up Spotify API Credentials (Required for Spotify Search):**
    
    -   This step is **only necessary if you want to use the "Spotify Search" feature** to find albums online. If you only plan to use the "Local JSON File" option, you can skip this step.
        
    -   Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/ "null") and create an application.
        
    -   Get your `Client ID` and `Client Secret`.
        
    -   In the project's root directory, create a new file named `.env`.
        
    -   Copy the content from `.env.example` into your new `.env` file.
        
    -   Replace the placeholder values in your `.env` file with your actual `Client ID` and `Client Secret`:
        
        ```
        SPOTIPY_CLIENT_ID=YOUR_CLIENT_ID
        SPOTIPY_CLIENT_SECRET=YOUR_CLIENT_SECRET        
        ```
        
    -   Add `.env` to your `.gitignore` file to prevent it from being uploaded to GitHub (important for security).
        
5.  **Add Font Files:**
    
    -   Place the `.otf` or `.ttf` font files used for poster drawing into the `fonts/` directory. Ensure they match the names specified in the `fonts` dictionary in `poster_core.py`.
        

## Running the Application

To run the application, open your terminal, navigate to the project's root directory, and execute the following command:

```
streamlit run gui.py
```

This command will start the Streamlit application and open it in your default web browser.

## Usage

1.  Once the application opens in your browser, you can select the **Language** from the sidebar.
    
2.  **Select Data Source:** Choose between searching Spotify or uploading a local JSON file.
    
3.  If you choose Spotify search, enter the album name and select one from the found albums.
    
4.  If you choose a local JSON file, upload a JSON file in the appropriate format.
    
5.  Select the source for the album cover: automatic download from URL (if available) or uploading a local image file.
    
6.  Use the **Poster Options** in the sidebar to adjust the poster size, tracks per column, tracklist horizontal position, and include copyright information.
    
7.  After setting the options, click the **Create Poster** button.
    
8.  The generated poster will be displayed on the screen. Click the **Download Poster** button to download the poster in PNG format.
    

## Multi-language Support

The application supports multiple languages by loading text strings from `.lang` files in the `lang/` directory.

To add a new language:

1.  Create a new `.lang` file in the `lang/` directory (e.g., `fr.lang` for French).
    
2.  Add translated strings for all keys found in the other `.lang` files, using the `key=value` format.
    
3.  Open the `languages.py` file.
    
4.  Add your new language and file path to the `LANGUAGES` dictionary:
    
    ```
    LANGUAGES = {
        "English🇺🇸": "lang/en.lang",
        "Türkçe🇹🇷": "lang/tr.lang",
        "Français🇫🇷": "lang/fr.lang" # Added new language
    }
    
    
    
    ```
    
5.  Restart the application, and the new language will appear in the language selection box in the sidebar.
    

## Contributing

Contributions are welcome! If you find any bugs or would like to add new features, please open an issue or submit a pull request.

## License

This project is licensed under the **GNU General Public License (GPL)**. See the `LICENSE` file for more details.

Feel free to adjust and expand upon this template based on your project's specific details. Remember to include any additional information relevant to your project, such as specific font files or example JSON files. Good luck!

# Guide to Run Lead Generation Software

## 1. Install Visual Studio Code
First, download and install [Visual Studio Code](https://code.visualstudio.com/). Visual Studio Code is a powerful code editor that will help you manage and run your project.

## 2. Install Python
Next, you need Python installed on your system. Download Python from [python.org](https://www.python.org/). Once the download is complete, run the installer and follow the setup instructions. Make sure to add Python to your system's environment variables. On Windows, you can do this by searching environment variables, go to System variables, find out the **path** and select it to edit, next add new path their of the location where python is installed adding the path (e.g., `C:\eg\eg\eg\python3.12`) to your system environment variables.

## 3. Open Visual Studio Code
Launch Visual Studio Code on your computer. To start working on your Lead Generation project, open the project directory within Visual Studio Code. This can be done by selecting **"Open Folder"** from the File menu and navigating to the directory containing your project files.

## 4. Install Required Extensions
- **Python Extension**: Go to the Extensions view by clicking on the Extensions icon in the sidebar or pressing `Ctrl+Shift+X`. Search for and install the **"Python"** extension by Microsoft.
- **Python Debugger Extension**: In the Extensions view, also search for and install the **"Python Debugger"** extension, which will help you debug your Python code.
- **Code Runner Extension**: Search for and install the **"Code Runner"** extension to run code snippets directly from Visual Studio Code.

## 5. Open the `server.py` File
In Visual Studio Code, locate and open the `server.py` file from your project. You will need to open the terminal within Visual Studio Code, which can be done by selecting **"Terminal"** from the top menu and then **"New Terminal"**.


## 6. Install Python Packages

In the terminal, run the following commands one by one to install the necessary Python packages for your project, Run all the follwoing commands in the given order:

**a. First, install Flask: Flask is a web framework that your project depends on.**
  
  ```bash
  python -m pip install flask
  ```
 
**b. Next, Run the Command install Playwright : Playwright is used for automating web browsers.**

  ```bash
  python -m pip install playwright
  ```
**c. Install BeautifulSoup4 : BeautifulSoup4 is a library for parsing HTML and XML documents.**

  ```bash
  python -m pip install beautifulsoup4
  ```
**d. Install Geopy using : Geopy provides geocoding functionalities.**

  ```bash
  python -m pip install geopy
  ```
**e. To ensure that Playwright is properly installed and up-to-date, run:**

  ```bash
  pip install --upgrade --force-reinstall playwright
  ```
**f. Finally, install the necessary browsers for Playwright by running:**

  ```bash
  python -m playwright install
  ```


## 7. Run Your Project
Open the `server.py` file in Visual Studio Code. Click the run button located at the top right corner of the editor. This action will open the output window, displaying the server’s URL. Click on the provided link or navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your web browser to see your project in action.

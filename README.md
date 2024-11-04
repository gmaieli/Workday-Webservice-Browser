# Web Service Browser for Workday API

This application is a Python-based GUI tool that allows users to browse and interact with the Workday API documentation. It enables users to view available web services and their operations, fetch XML content, and perform actions like copying and saving the XML data.

## Features

- **Browse Web Services**: Select from a list of available web services and their operations.
- **View XML Content**: Fetch and display XML content with syntax highlighting.
- **Copy to Clipboard**: Easily copy the entire XML content or selected text to the clipboard.
- **Save to File**: Save the XML content to a local file.
- **Documentation Access**: Quick access to the Workday API documentation for further reference.

## Requirements

To run this application, you need to have Python installed on your machine along with the following libraries:

- `requests`
- `beautifulsoup4`
- `tkinter` (comes pre-installed with Python)
- `pyperclip`
- `Pillow`

You can install the required libraries using pip:

```shell
pip install requests beautifulsoup4 pillow pyperclip
```
## Usage
1. Clone the repository to your local machine:
```shell
git clone https://github.com/yourusername/web-service-browser.git
cd web-service-browser
```
2. Run the application
```shell
python main.py
```
## Contributing
Contributions are welcome! If you have suggestions for improvements or find bugs, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/gmaieli/Workday-Webservice-Browser/blob/main/LICENSE) file for details.

## Acknowledgments
- Thanks to the Workday community for providing the API documentation.
- Special thanks to the developers of the libraries used in this project.

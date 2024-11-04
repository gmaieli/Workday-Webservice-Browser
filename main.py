import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import pyperclip
import re
from PIL import Image, ImageTk
import platform  

# URL of Webservice API Documentation used for parsing all Services and Operations
url = "https://community.workday.com/sites/default/files/file-hosting/productionapi/operations/index.html"

# Extract version from the webpage
def extract_version():
    global version
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        html_content = response.text
        
        # Search for the version in the HTML content
        version_match = re.search(r'Operation Directory: \(v([\d.]+) /', html_content)
        if version_match:
            version = f"v{version_match.group(1)}"
        else:
            raise ValueError("Version not found in the document.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error connecting to the website: {e}")
    except ValueError as ve:
        messagebox.showerror("Error", str(ve))

# Extract web services
def extract_webservices():
    global version  # Use the global version variable
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")
        webservices = {}
        for row in rows[1:]:
            cells = row.find_all("td")
            webservice_operation = cells[0].find("a").text.strip()
            webservice_service = cells[2].find("a").text.strip()
            if webservice_service not in webservices:
                webservices[webservice_service] = []
            webservices[webservice_service].append(webservice_operation)
        return webservices
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error connecting to the website: {e}")
        return {}

# Function called when a web service is selected
def variable_selected(event):
    selected_service = variable_dropdown.get()
    operations = webservices.get(selected_service, [])
    operation_dropdown['values'] = operations
    operation_dropdown.set('')  # Clear the operation dropdown

# Function to fetch and display XML content with syntax highlighting
def fetch_xml_content():
    selected_operation = operation_dropdown.get()
    selected_service = variable_dropdown.get()
    if selected_operation:
        webservice_url = base_url.format(selected_service, selected_operation)
        documentation_url = f"https://community.workday.com/sites/default/files/file-hosting/productionapi/{selected_service}/{version}/{selected_operation}.html"
        
        try:
            response = requests.get(webservice_url)
            response.raise_for_status()  # Raise an error for bad responses
            xml_content = response.text
            
            # Display highlighted XML content in the text area
            display_highlighted_xml(xml_content)
            
            # Update documentation button
            doc_button.config(state=tk.NORMAL)  # Enable the button
            doc_button.bind("<Button-1>", lambda e: open_url(documentation_url))  # Make the button clickable
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Error connecting to the web service: {e}")

# Function to display highlighted XML content
def display_highlighted_xml(xml_content):
    text_area.delete(1.0, tk.END)  # Clear previous content

    # Insert raw XML content
    text_area.insert(tk.END, xml_content)

    # Define regex patterns for highlighting
    comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)  # Matches comments
    tag_pattern = re.compile(r'<(/?)(\w+)(.*?)>', re.DOTALL)  # Matches opening and closing tags
    attr_pattern = re.compile(r'(\w+:?\w*)="(.*?)"')  # Matches attributes with optional prefix

    # Highlight comments
    for match in comment_pattern.finditer(xml_content):
        start, end = match.span()
        text_area.tag_add("comment", "1.0 + {} chars".format(start), "1.0 + {} chars".format(end))

    # Highlight tags and attributes
    for match in tag_pattern.finditer(xml_content):
        start, end = match.span()
        text_area.tag_add("tag", "1.0 + {} chars".format(start), "1.0 + {} chars".format(end))

        # Highlight attributes within the tag
        attr_string = match.group(0)
        for attr_match in attr_pattern.finditer(attr_string):
            attr_start, attr_end = attr_match.span()
            text_area.tag_add("attribute", "1.0 + {} chars".format(start + attr_start), "1.0 + {} chars".format(start + attr_end))

    # Configure tag colors
    text_area.tag_configure("tag", foreground="#5FC8FD")  # Tags in blue
    text_area.tag_configure("comment", foreground="#66DF66")  # Comments in green
    text_area.tag_configure("attribute", foreground="#FF8D54")  # Attributes in orange

# Function to copy text to clipboard
def copy_to_clipboard():
    text = text_area.get(1.0, tk.END)  # Get all text from the text area
    pyperclip.copy(text)  # Copy text to clipboard
    show_temporary_message("XML content copied to clipboard!")

# Function to copy selected text
def copy_selected_text():
    try:
        selected_text = text_area.get(tk.SEL_FIRST, tk.SEL_LAST)  # Get selected text
        pyperclip.copy(selected_text)  # Copy to clipboard
        show_temporary_message("Selected XML content copied to clipboard!")
    except tk.TclError:
        messagebox.showwarning("Warning", "No text selected to copy!")

# Function to show a temporary message
def show_temporary_message(message):
    temp_message = tk.Toplevel(root)  # Create a new top-level window
    temp_message.title("Info")
    
    # Create a label for the message
    label = tk.Label(temp_message, text=message, padx=20, pady=20)
    label.pack()
    
    # Center the temporary message window
    temp_message_width = 300
    temp_message_height = 100
    screen_width = temp_message.winfo_screenwidth()
    screen_height = temp_message.winfo_screenheight()
    x = (screen_width // 2) - (temp_message_width // 2)
    y = (screen_height // 2) - (temp_message_height // 2)
    temp_message.geometry(f"{temp_message_width}x{temp_message_height}+{x}+{y}")
    
    temp_message.after(2000, temp_message.destroy)  # Close after 2 seconds

# Function to save XML content to a file
def save_to_file():
    xml_content = text_area.get(1.0, tk.END)  # Get all text from the text area
    if xml_content.strip():  # Check if there's content to save
        file_path = filedialog.asksaveasfilename(defaultextension=".xml",
                                                   filetypes=[("XML files", "*.xml"),
                                                              ("All files", "*.*")])
        if file_path:  # If the user didn't cancel the dialog
            with open(file_path, 'w') as file:
                file.write(xml_content)  # Write the content to the file
            show_temporary_message("XML content saved successfully!")  # Show saved message
    else:
        messagebox.showwarning("Warning", "No content to save!")

# Function called when the Search button is clicked or Enter key is pressed
def search():
    fetch_xml_content()

# Function to open the documentation link in a web browser
def open_url(url):
    webbrowser.open(url)

# Function to show the context menu
def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

# Tooltip class
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window is not None:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.text, background="lightgrey", foreground="black", borderwidth=1, relief="solid")
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# Call the function to extract the version before extracting web services
extract_version()
webservices = extract_webservices()

# URL of the webpage with the web service content
base_url = f"https://community.workday.com/sites/default/files/file-hosting/productionapi/{{}}/{version}/samples/{{}}_Request.xml"

# Create GUI
root = tk.Tk()
root.title("Web Service Browser")

# Set the initial size of the window (width x height)
initial_width = 800  # Base width
initial_height = 600  # Base height
root.geometry(f"{int(initial_width * 1.5)}x{int(initial_height * 1.5)}")  # 50% larger

# Frame for dropdowns
frame = tk.Frame(root)
frame.pack(pady=10, fill=tk.X)

# Label for web service variable
variable_label = tk.Label(frame, text="Select Web Service:")
variable_label.grid(row=0, column=0, sticky='w')  # Align left

# Dropdown for web service variable (sorted alphabetically)
variable_dropdown = ttk.Combobox(frame, values=sorted(webservices.keys()), width=30)  
variable_dropdown.bind("<<ComboboxSelected>>", variable_selected)
variable_dropdown.grid(row=0, column=1, padx=(5, 0))  # Add space to the left
variable_dropdown['height'] = 20

# Label for operations
operation_label = tk.Label(frame, text="Select Operation:")
operation_label.grid(row=1, column=0, sticky='w')  # Align left

# Dropdown for operations
operation_dropdown = ttk.Combobox(frame, values=[], width=30)  
operation_dropdown.grid(row=1, column=1, padx=(5, 0))  # Add space to the left
operation_dropdown['height'] = 20

# Button for Search
search_button = tk.Button(frame, text="Search", command=search)
search_button.grid(row=2, column=1, sticky='e', padx=(5, 0))  # Right-align the button

# Bind Enter key to the search function
root.bind('<Return>', lambda event: search())

# Text area to display XML content with scroll functionality
text_area = tk.Text(root, wrap=tk.NONE, bg="#3C3C3C", fg="#E5E5E5", font=("Sans Serif", 12))
text_area.pack(pady=10, fill=tk.BOTH, expand=True)

# Create context menu
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Copy", command=copy_selected_text)

# Check the operating system and bind mouse buttons
if platform.system() == "Darwin":  # macOS
    text_area.bind("<Button-2>", show_context_menu)  # Middle mouse button
else:  # Windows and others
    text_area.bind("<Button-3>", show_context_menu)  # Right-click

# Button for documentation link
doc_button = tk.Button(root, text="To access the Workday Documentation click here", fg="blue", command=lambda: open_url(""))
doc_button.pack(pady=5)
doc_button.config(state=tk.DISABLED)  # Initially disable the button

# Load the copy icon
copy_icon = Image.open("copy_icon.png")  # Use a PNG file
copy_icon = copy_icon.resize((20, 20), Image.LANCZOS)  # Resize the icon
copy_icon = ImageTk.PhotoImage(copy_icon)

# Load the save icon
save_icon = Image.open("save_icon.png")  # Use a PNG file for save
save_icon = save_icon.resize((20, 20), Image.LANCZOS)  # Resize the icon
save_icon = ImageTk.PhotoImage(save_icon)

# Copy button positioned at the upper right corner of the text area
copy_button = tk.Button(root, image=copy_icon, command=copy_to_clipboard, borderwidth=0)
copy_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)  # Adjust x and y for padding

# Save button positioned below the copy button with an icon
save_button = tk.Button(root, image=save_icon, command=save_to_file, borderwidth=0)
save_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=40)  # Adjust y for spacing

# Add tooltips
ToolTip(copy_button, "Copy")
ToolTip(save_button, "Save")

# Start GUI
root.mainloop()

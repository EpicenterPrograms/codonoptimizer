'''
This allows optimizing codons to multiple organisms (or just one)
'''

__author__ = "Robert Benson"
__date__ = "2023"

import site
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.font import Font
import random
import math
import threading
import webbrowser

bg = "black"
fg = "white"



'''
class WidgetObject:
	def __init__ (self, widget, identifier):
		self.widget = widget
		self.id = identifier
'''

def list_to_string(list_to_convert, separator):
	s = ""
	for item in list_to_convert:
		s += separator + str(item)
	return s[len(separator):]

def print_attributes(widget):
	print("Attribute list of {}:".format(widget))
	for key in widget.keys():
		print("Attribute: {:<20}".format(key), end=" ")
		value = widget[key]
		vtype = type(value)
		print("Type: {:<30} Value: {}".format(str(vtype), value))
		
def resize_to_text(widget, update=None):
	'''
	matches a widget to the size of its text
	'''
	if "bold" in widget.cget("font").split():  # if the font is bolded
		font = Font(weight="bold")
	else:
		font = Font()
	if isinstance(widget, tk.Entry):
		info = widget.get()
		if info != "":  # if there's something to resize to
			longest_length = float(max([font.measure(line) for line in info.splitlines()]))  # the line of text that takes up the most space
			widget_width = math.ceil(longest_length / font.measure("c"))  # converts pixels into font size units ("c" is relatively arbitrary, but font_size can't substitute)
			widget.config(width=widget_width)  # fit the widget to the text
	else:
		info = widget.get(1.0, "end")
		longest_length = float(max([font.measure(line) for line in info.splitlines()]))  # the line of text that takes up the most space
		widget_width = math.ceil(longest_length / font.measure("c"))  # converts pixels into font size units ("c" is relatively arbitrary, but font_size can't substitute)
		# widget_height = info.count("\n")  # counts the number of lines of text
		widget_height = int(widget.index("end-1c").split(".")[0])  # counts the number of lines of text
		widget.config(width=widget_width, height=widget_height)  # fit the widget to the text
	if not update == None and not update == False:
		update.update_scroll_region()
		
def add_text(widget, text, update=None):
	if update == None:
		update = gui
	widget.insert("end", text)
	resize_to_text(widget, update=update)



class ScrollableText:
	def __init__(self, parent, words, font_size, width=None, height=None, justify="center", style="", **extras):
		# Create a container for the text and a potential scrollbar
		self.container = tk.Frame(parent)
		# Create the Text widget with word wrapping
		self.text = tk.Text(self.container, height=(words.count("\n")+1), font=("",font_size,style), relief="flat", wrap="word", foreground=fg, background=bg, **extras)
		self.text.tag_config("justification", justify=justify)
		self.text.insert(1.0, words)
		self.text.config(state="disabled")  # prevents the user from editing the text (has to come after inserting the text)
		self.text.tag_add("justification", "1.0", "end")
		resize_to_text(self.text)
		if width:
			self.text.config(width=width)
		if height:
			self.text.config(height=height)
		self.text.pack(side="left", fill="both", expand=True)
		
		# Create the vertical scrollbar
		self.scrollbar = tk.Scrollbar(self.container, command=self.text.yview)
		### self.root.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(round(-event.delta / 100), "units"))
		self.text.config(yscrollcommand=self.scrollbar.set)
		
		# Bind the configure event to check for overflow
		self.text.bind("<Configure>", self.check_overflow)
		
	def pack(self, **extras):
		self.container.pack(**extras)
		
	def grid(self, **extras):
		self.container.grid(**extras)
		
	def place(self, **extras):
		self.container.place(**extras)

	def check_overflow(self, event=None):
		self.text.update_idletasks()
		# Get the widget height in pixels
		widget_height = self.text.winfo_height()
		# Iterate over each line to find the last visible one
		line_index = 1
		while True:
			bbox = self.text.dlineinfo(f"{line_index}.0")  # Get bounding box for the line
			if not bbox:  # No more lines
				break
			line_top, line_height = bbox[1], bbox[3]
			if line_top + line_height > widget_height:  # Line exceeds visible area
				break
			line_index += 1
		# The last visible line is one less than the current line_index
		last_visible_line = line_index - 1
		# Get the total number of lines in the Text widget
		total_lines = int(self.text.index("end-1c").split(".")[0])
		# Check if the total lines exceed the last visible line
		if total_lines > last_visible_line:
			if not self.scrollbar.winfo_ismapped():  # If the scrollbar isn't visible
				self.scrollbar.pack(side="right", fill="y")
				self.text.pack(side="left", fill="both", expand=True)
		else:
			if self.scrollbar.winfo_ismapped():  # If the scrollbar is visible
				self.scrollbar.pack_forget()
				self.text.pack(side="left", fill="both", expand=True)
					
	def replace_text(self, new_text, resize=False):
		'''
		Simplifies the unnecessarily difficult task of replacing the text of a disabled Text object
		'''
		self.text.config(state="normal")
		self.text.delete(1.0, "end")
		self.text.insert(1.0, new_text)
		self.text.tag_add("center", "1.0", "end")
		if resize:
			### self.text.config(height=(new_text.count("\n")+1))
			resize_to_text(self.text)
		self.text.config(state="disabled")
		self.check_overflow()



class GUI:
	gui_wrapper = None
	root = tk.Tk()  # creates and holds an instance of the tk window
	canvas = tk.Canvas(root, background=bg, bd=0, highlightthickness=0)  # creates a widget which can handle scrolling
	canvas.pack(side="left", fill="both", expand=True)  # adds the canvas to the window
	### canvas.place(relx=.5, rely=.5, anchor="center")
	window = tk.Frame(canvas, bg=bg)  # creates a widget to hold everything to be scrollable
	window_id = canvas.create_window((canvas.winfo_screenwidth() / 2, 0), window=window, anchor="center")  # actually adds the Frame to the Canvas
	
	def update_scroll_region(self, *event):
		'''
		makes sure changes to the GUI result in changes to what can be scrolled
		needs to be called after every action that could change the size of the GUI
		*event = a placeholder argument to prevent errors when this is used with an event listener
		'''
		self.canvas.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox("all"))  # identifies the region of the Canvas that should be scrollable

	def __init__ (self, title="Default Title", width=root.winfo_screenwidth(), height=root.winfo_screenheight(), background=bg):
		# width="<widthpixels>", height="<heightpixels>"
		'''
		initializes the Tk window
		
		title = title
		width = Canvas Width
		height = Canvas Height
		(width and height need to be floats)
		background = background of the canvas
		'''
		
		self.gui_wrapper = self
		
		self.root.wm_title(title)
		self.root.configure(background=background)
		# window.wm_overrideredirect(1)
		# window.focus_set()

		self.canvas.bind("<Configure>", self.update_scroll_region)  # makes sure the scrollable region of the Canvas updates with new content
		
		self.cw = float(width)  # canvas width in pixels
		self.ch = float(height)  # canvas height in pixels
		self.unit = self.ch/255 if self.ch<self.cw else self.cw/255  # sets the canvas units (calibrated to the smallest dimension of the screen)
		self.max_x = self.cw/self.unit  # the maximum displayed x-value in canvas units
		self.max_y = self.ch/self.unit  # the maximum displayed y-value in canvas units
		self.pressed_keys = {}  # the keys currently pressed
		
		### self.canvas = tk.Canvas(self.window, width=self.cw, height=self.ch, background=background)
		### self.canvas.grid()

		self.widget_list = [self.canvas, self.window]
		self.radiobutton_groups = {}
		
	def calculate_text_dimensions(self, text):
		# Get the bounding box of the text content
		bbox = text.bbox("all")
		# Calculate the width and height based on the bounding box
		width = bbox[2] - bbox[0]
		height = bbox[3] - bbox[1]
		return width, height
	
	def center_window(self):
		# Ensure the canvas is updated
		self.canvas.update_idletasks()
		# Get the size of the window
		window_width = self.window.winfo_reqwidth()
		window_height = self.window.winfo_reqheight()
		# Get the size of the canvas
		canvas_width = self.canvas.winfo_width()
		canvas_height = self.canvas.winfo_height()
		# Calculate the center coordinates
		x_center = (canvas_width - window_width) // 2
		y_center = (canvas_height - window_height) // 2
		# Move the window to the center
		self.canvas.coords(self.window_id, x_center, y_center)
		
	def set_icon(self, path):
		self.root.iconbitmap(path)

	def make_scrollbar(self, parent, orient="vertical", **extras):
		if orient == "vertical":
			scroll = tk.Scrollbar(self.root, orient=orient, command=self.canvas.yview)
			self.canvas.config(yscrollcommand=scroll.set)
			scroll.pack(side="right", fill="y")
			self.root.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(round(-event.delta / 100), "units"))
		elif orient == "horizontal":
			scroll = tk.Scrollbar(self.root, orient=orient, command=self.canvas.xview)
			self.canvas.config(xscrollcommand=scroll.set)
			scroll.pack(side="bottom", fill="x")
			self.root.bind("<Shift-MouseWheel>", lambda event: self.canvas.xview_scroll(round(-event.delta / 100), "units"))
		else:
			raise ValueError('The value of "orient" must be either "vertical" or "horizontal".')
		return scroll

	def make_text(self, words, font_size, parent=window, width=None, height=None, justify="center", style="", **extras):
		'''
		creates text
		
		"words" needs to be a string
		default justification is center
		'''
		'''
		widget = tk.Text(parent, height=(words.count("\n")+1), font=("",int(self.unit*font_size),style), relief="flat", wrap="word", foreground=fg, background=bg, **extras)
		widget.tag_config("justification", justify=justify)
		widget.insert(1.0, words)
		widget.config(state="disabled")  # prevents the user from editing the text (has to come after inserting the text)
		widget.tag_add("justification", "1.0", "end")
		### identifier = self.canvas.create_window(x*self.unit, y*self.unit, window=widget)
		resize_to_text(widget)
		if width:
			widget.config(width=width)
		if height:
			widget.config(height=height)
		text = widget  ### WidgetObject(widget, identifier)
		'''
		text = ScrollableText(parent, words, int(self.unit*font_size), width=width, height=height, justify=justify, style=style, **extras)
		self.widget_list.append(text.text)
		return text
	
	def make_entry(self, parent=window, placeholder="", **extras):
		'''
		creates a text input for user input
		use entry_reference.is_empty() to return a boolean of whether the input is empty (or has the placeholder value)
		'''
		widget = tk.Entry(parent, relief="flat", borderwidth=1, highlightbackground=fg, highlightcolor="blue", highlightthickness=1, background=bg, foreground=fg, insertbackground=fg, **extras)
		### identifier = self.canvas.create_window(x*self.unit, y*self.unit, window=widget)
		input_box = widget  ### WidgetObject(widget, identifier)
		if not placeholder == "":
			input_box.insert(0, placeholder)
			def focusIn(_):
				if input_box.get() == placeholder:
					input_box.delete(0, tk.END)
			def focusOut(_):
				if input_box.get() == "":
					input_box.insert(0, placeholder)
			input_box.bind("<FocusIn>", focusIn)
			input_box.bind("<FocusOut>", focusOut)
		input_box.is_empty = lambda: input_box.get() == "" or input_box.get() == placeholder
		self.widget_list.append(input_box)
		return input_box

	def make_button(self, text, command, parent=window, **extras):
		'''
		creates a button which can execute a certain function
		'''
		button = tk.Button(parent, text=text, command=command, cursor="hand2", **extras)
		### identifier = self.canvas.create_window(x*self.unit, y*self.unit, window=button)
		self.widget_list.append(button)
		return button

	def make_frame(self, parent=window, width=10, height=50, padx=2, pady=2, **extras):
		'''
		creates a generic box
		'''
		widget = tk.Frame(parent, width=width, height=height, background=bg, padx=padx, pady=pady, **extras)
		### identifier = self.canvas.create_window(x*self.unit, y*self.unit, window=widget)
		frame = widget  ### WidgetObject(widget, identifier)
		'''
		def add_child(item):
			if isinstance(item, int):  # if the canvas identifier is provided
				self.canvas.itemconfigure(item, window=widget)
			elif isinstance(item, WidgetObject):  # if the widget is created with one of my functions
				item.widget.grid_forget()
				item.widget.grid(row=0, column=0)
				self.canvas.itemconfigure(item.id, window=frame.widget)
			else:
				raise TypeError("The canvas identifier couldn't be found.")

		frame.add_child = add_child
		'''
		self.widget_list.append(frame)
		return frame
	
	def make_gradient_frame(self, parent=window):
		pass
	
	def make_checkbutton(self, label, selected=False, cursor="hand2", parent=window, **extras):
		'''
		creates a checkbox
		use checkbutton_reference.is_selected() to retrieve a boolean of whether the box is checked or not
		'''
		checked = tk.BooleanVar(value=selected)
		checkbox = tk.Checkbutton(parent, text=label, variable=checked, bg=bg, fg=fg, selectcolor=bg, cursor=cursor, **extras)
		checkbox.is_selected = checked.get
		self.widget_list.append(checkbox)
		return checkbox
	
	def make_radiobutton(self, grouping, value, label, selected=False, cursor="hand2", parent=window, **extras):
		'''
		creates a radio button

		grouping = the name of the group the radio button belongs to
		value = the value of the radio button
		label = the text to display next to the radio button
		'''
		if grouping not in self.radiobutton_groups:
			self.radiobutton_groups[grouping] = tk.StringVar()
		radio = tk.Radiobutton(parent, text=label, variable=self.radiobutton_groups[grouping], value=value, bg=bg, fg=fg, selectcolor=bg, cursor=cursor, **extras)
		if selected:
			self.radiobutton_groups[grouping].set(value)
		self.widget_list.append(radio)
		return radio
	
	def make_option_menu(self, options, selected=None, parent=window, **extras):
		'''
		creates a box which can show a dropdown with options to choose from
		
		options = a list of string options
		selected = the index of the option to display
		'''
		# Create a StringVar to store the selected option
		variable = tk.StringVar(parent)
		if selected != None:
			variable.set(options[options.index(selected)])  # Set the default value
		else:
			variable.set(options[0])  # Set the default value
		# Create the OptionMenu
		dropdown = tk.OptionMenu(parent, variable, *options, **extras)
		dropdown._selection = variable
		'''
		# Bind the selection event to a function
		def on_select(*_):
			print(dropdown._selection.get())
		dropdown._selection.trace("w", on_select)
		'''
		self.widget_list.append(dropdown)
		return dropdown
		
	def make_labeled_entry(self, label, parent=window, label_side="left", font_size=4, placeholder="", resize_entry=False, entry_width=20):
		frame = tk.Frame(parent, background=bg)
		if label_side == "left":
			text = self.make_text(label, font_size, parent=frame, justify="right")
			text.grid(row=0, column=0, padx=(0,5))
			entry = self.make_entry(parent=frame, placeholder=placeholder, width=entry_width)
			entry.grid(row=0, column=1)
		elif label_side == "right":
			entry = self.make_entry(parent=frame, placeholder=placeholder, width=entry_width)
			entry.grid(row=0, column=0)
			text = self.make_text(label, font_size, parent=frame, justify="left")
			text.grid(row=0, column=1, padx=(5,0))
		else:
			raise ValueError('The label_side must be "left" or "right".')
		'''  # functionality replicated by width=0
		if resize_entry:
			# resizes the entry while typing
			entry.bind("<KeyRelease>", lambda event, c=entry: resize_to_text(c, update=self.gui_wrapper))
			entry.bind("<<Cut>>", lambda event, c=entry: resize_to_text(c, update=self.gui_wrapper))
			entry.bind("<<Paste>>", lambda event, c=entry: resize_to_text(c, update=self.gui_wrapper))
		'''
		self.widget_list.append(frame)
		self.widget_list.append(text.text)
		self.widget_list.append(entry)
		frame.text = text
		frame.get_label = lambda: text.text.get(1.0, "end-1c")
		frame.entry = entry
		return frame
	
	def pack_padding(self, *lines, parent=window):
		'''
		adds some spacing between packed widgets
		'''
		if len(lines) > 0 and isinstance(lines[0], int):
			lines = lines[0]
		else:
			lines = 1
		spacing = tk.Label(parent, background=bg, height=lines)
		spacing.pack()
		self.widget_list.append(spacing)
		return spacing

	def modify(self, item, **modifications):
		'''
		modifies items on the canvas
		'''
		if isinstance(item, int):  # if the item is an integer ID of something on the canvas
			self.canvas.itemconfig(item, **modifications)
		elif item.winfo_exists():  # if the item is a widget
			item.config(**modifications)
			'''
		elif isinstance(item, WidgetObject):  # if it's a widget created with one of my functions
			item.widget.config(**modifications)
			'''
		else:
			raise TypeError("The item to modify has an unrecognized type.")
		
	def change_theme(self, preset=None, background=bg, foreground=fg):
		# uses a present if specified
		match preset:
			case "light":
				background = "white"
				foreground = "black"
			case "dark":
				background = "black"
				foreground = "white"
		# changes the colors of all of the widgets
		for widget in self.widget_list:
			match widget.winfo_class():
				case "Radiobutton" | "Checkbutton":
					widget.config(bg=background, fg=foreground, selectcolor=background)
				case "Menubutton" | "Button":
					pass
					if isinstance(widget, tk.OptionMenu):
						pass
					else:
						pass
				case "Entry":
					widget.config(highlightbackground=foreground, background=background, foreground=foreground, insertbackground=foreground)
				case "Frame" | "Canvas":
					widget.config(bg=background)
				case _:
					try:
						widget.config(bg=background, fg=foreground)
					except tk.TclError:  # if setting the colors isn't supported
						pass
	
	def key_pressed(self, event):
		'''
		this says when a key is pressed
		'''
		self.pressed_keys[event.keysym] = True
	
	def key_released(self, event):
		'''
		this says when a key is released
		'''
		self.pressed_keys[event.keysym] = False
	"""
	def registerKeys(*keys) :
		'''
		binds all used keys
		the keysym of the key you want should be used
		a checking function should use "pressedKeys" to determine if a key is pressed and act accordingly
		'''
		global window, pressedKeys
		keyList = []
		for key in keys :
			keyList.append(key)
		for key in keyList :
			window.bind("<KeyPress-{}>".format(key), keyPressed)
			window.bind("<KeyRelease-{}>".format(key), keyReleased)
			pressedKeys[key] = False
	"""
	def record_key_presses(self):
		'''
		allows keeping track of which keys are pressed at a given time
		'''
		self.window.bind("<KeyPress>", self.key_pressed)
		self.window.bind("<KeyRelease>", self.key_released)
	
	def close(self, *event):
		'''
		closes the window
		has *event just in case it's used in a key binding
		'''
		self.window.destroy()
	
	def appear(self):
		'''
		starts tk's main loop
		make sure this is last
		'''
		self.root.geometry("{0}x{1}".format(round(self.cw/2), round(self.ch/2)))  # sets the window size when not filling the screen
		self.root.state("zoomed")  # maximizes the window
		self.root.focus_force()  # focuses the window
		# root.attributes("-fullscreen", True)
		self.root.mainloop()

def replace_text(widget, new_text, resize=True):  ## putting this before the classes makes it not be recognized
	'''
	Simplifies the unnecessarily difficult task of replacing the text of a disabled Text object
	'''
	widget.config(state="normal")
	widget.delete(1.0, "end")
	widget.insert(1.0, new_text)
	widget.tag_add("center", "1.0", "end")
	if resize:
		widget.config(height=(new_text.count("\n")+1))
	widget.config(state="disabled")

def set_placeholder(widget, placeholder):
	'''
	sets placeholders for text inputs
	'''
	widget.insert(0, placeholder)
	def focusIn(_):
		if widget.get() == placeholder:
			widget.delete(0, tk.END)
	def focusOut(_):
		if widget.get() == "":
			widget.insert(0, placeholder)
	widget.bind("<FocusIn>", focusIn)
	widget.bind("<FocusOut>", focusOut)

def count_overlapping(string, sub_str, return_indices=False):
	sub_str_len = len(sub_str)
	occurrences = 0
	indices = []
	for i in range(len(string)):
		if string[i:i+sub_str_len] == sub_str:
			occurrences += 1
			indices.append(i)
	if return_indices:
		return occurrences, indices
	else:
		return occurrences

def find_overlapping(string, sub_str):
	sub_str_len = len(sub_str)
	indices = []
	for i in range(len(string)):
		if string[i:i+sub_str_len] == sub_str:
			indices.append(i)
	return indices

def compare_iterables(source, target):
	'''
	Compute the Levenshtein distance between two iterables.

	The Levenshtein distance is the number of changes needed to transform one
	iterable into the other, where each change can be a substitution, insertion,
	or deletion of an element.

	Parameters
	----------
	source: iterable
		The first iterable to compare.
	target: iterable
		The second iterable to compare.

	Returns
	-------
	int
		The Levenshtein distance between `source` and `target`.
	'''
	# Create a 2D matrix to store the Levenshtein distances between prefixes of the iterables.
	matrix = [[0] * (len(target) + 1) for _ in range(len(source) + 1)]
	# Initialize the first row and column of the matrix.
	for i, s in enumerate(source):
		matrix[i + 1][0] = i + 1
	for j, t in enumerate(target):
		matrix[0][j + 1] = j + 1
	# Fill the rest of the matrix by computing the Levenshtein distance between prefixes.
	for i, s in enumerate(source):
		for j, t in enumerate(target):
			substitution_cost = 0 if s == t else 1
			matrix[i + 1][j + 1] = min(
				matrix[i][j + 1] + 1,  # deletion
				matrix[i + 1][j] + 1,  # insertion
				matrix[i][j] + substitution_cost  # substitution
				)
	# The Levenshtein distance is the bottom-right element of the matrix.
	return matrix[-1][-1]



aa_dict = {
	"a": ["gca", "gcg", "gcc", "gct"],
	"c": ["tgc", "tgt"],
	"d": ["gac", "gat"],
	"e": ["gaa", "gag"],
	"f": ["ttc", "ttt"],
	"g": ["gga", "ggg", "ggc", "ggt"],
	"h": ["cac", "cat"],
	"i": ["ata", "atc", "att"],
	"k": ["aaa", "aag"],
	"l": ["cta", "ctg", "ctc", "ctt", "tta", "ttg"],
	"m": ["atg"],
	"n": ["aac", "aat"],
	"o": ["???"],  # non-canonical amino acid
	"p": ["cca", "ccg", "ccc", "cct"],
	"q": ["caa", "cag"],
	"r": ["aga", "agg", "cga", "cgg", "cgc", "cgt"],
	"s": ["agc", "agt", "tca", "tcg", "tcc", "tct"],
	"t": ["aca", "acg", "acc", "act"],
	"u": ["tga"],  # non-canonical amino acid
	"v": ["gta", "gtg", "gtc", "gtt"],
	"w": ["tgg"],
	"y": ["tac", "tat"],
	"*": ["taa", "tag", "tga"]
	}

### Check Kazusa / Codon Usage Database or HIVE-CUT
## aliivibrio		= Aliivibrio fischeri (bioluminescent bacterium)
## arabidopsis		= Arabidopsis thaliana (small flower)
## bacillus			= Bacillus subtilis (gram-positive bacterium)
## caenorhabditis	= Caenorhabditis elegans (roundworm)
## danio			= Danio rerio (fish)
## deinococcus		= Deinococcus radiodurans R1 (radiation-tolerant bacterium)
## drosophila		= Drosophila melanogaster (fruit fly)
## escherichia		= Escherichia coli (gram-negative bacterium)
## haloferax		= Haloferax volcanii (archeon)
## homo				= Homo sapiens (human)
## hydra			= Hydra vulgaris (hydra)
## oryza			= Oryza sativa (rice)
## physcomitrella	= Physcomitrella patens (moss)
## populus			= Populus trichocarpa (tree)
## procambarus		= Procambarus clarkii (crayfish)
## pyrocystis		= Pyrocystis fusiformis (bioluminescent diatom)
## saccaromyces		= Saccaromyces cerevisiae (yeast)
## synechocystis	= Synechocystis sp. PCC 6803 (cyanobacterium)
## vibrio			= Vibrio natriegens (extremely fast-growing bacterium)
codon_dict = {
	"aaa": { "aa": "k", "Escherichia coli": 0.71, "Saccaromyces cerevisiae": 0.58, "Bacillus subtilis": 0.70, "Homo sapiens": 0.43, "Arabidopsis thaliana": 0.49, "Procambarus clarkii": 0.36, "Caenorhabditis elegans": 0.59, "Aliivibrio fischeri": 0.78, "Pyrocystis fusiformis": 0.24, "Drosophila melanogaster": 0.30, "Physcomitrella patens": 0.35, "Synechocystis sp. PCC 6803": 0.70, "Deinococcus radiodurans R1": 0.29, "Danio rerio": 0.49, "Oryza sativa": 0.33, "Populus trichocarpa": 0.51, "Haloferax volcanii": 0.22, "Hydra vulgaris": 0.78, "Vibrio natriegens": 0.68 },
	"aag": { "aa": "k", "Escherichia coli": 0.29, "Saccaromyces cerevisiae": 0.42, "Bacillus subtilis": 0.30, "Homo sapiens": 0.57, "Arabidopsis thaliana": 0.51, "Procambarus clarkii": 0.64, "Caenorhabditis elegans": 0.41, "Aliivibrio fischeri": 0.22, "Pyrocystis fusiformis": 0.76, "Drosophila melanogaster": 0.70, "Physcomitrella patens": 0.65, "Synechocystis sp. PCC 6803": 0.30, "Deinococcus radiodurans R1": 0.71, "Danio rerio": 0.51, "Oryza sativa": 0.67, "Populus trichocarpa": 0.49, "Haloferax volcanii": 0.78, "Hydra vulgaris": 0.22, "Vibrio natriegens": 0.32 },
	"aac": { "aa": "n", "Escherichia coli": 0.41, "Saccaromyces cerevisiae": 0.41, "Bacillus subtilis": 0.44, "Homo sapiens": 0.53, "Arabidopsis thaliana": 0.48, "Procambarus clarkii": 0.69, "Caenorhabditis elegans": 0.38, "Aliivibrio fischeri": 0.36, "Pyrocystis fusiformis": 0.67, "Drosophila melanogaster": 0.56, "Physcomitrella patens": 0.53, "Synechocystis sp. PCC 6803": 0.37, "Deinococcus radiodurans R1": 0.84, "Danio rerio": 0.60, "Oryza sativa": 0.55, "Populus trichocarpa": 0.36, "Haloferax volcanii": 0.96, "Hydra vulgaris": 0.29, "Vibrio natriegens": 0.56 },
	"aat": { "aa": "n", "Escherichia coli": 0.59, "Saccaromyces cerevisiae": 0.59, "Bacillus subtilis": 0.56, "Homo sapiens": 0.47, "Arabidopsis thaliana": 0.52, "Procambarus clarkii": 0.31, "Caenorhabditis elegans": 0.62, "Aliivibrio fischeri": 0.64, "Pyrocystis fusiformis": 0.33, "Drosophila melanogaster": 0.44, "Physcomitrella patens": 0.47, "Synechocystis sp. PCC 6803": 0.63, "Deinococcus radiodurans R1": 0.16, "Danio rerio": 0.40, "Oryza sativa": 0.45, "Populus trichocarpa": 0.64, "Haloferax volcanii": 0.04, "Hydra vulgaris": 0.71, "Vibrio natriegens": 0.44 },
	"aga": { "aa": "r", "Escherichia coli": 0.13, "Saccaromyces cerevisiae": 0.48, "Bacillus subtilis": 0.25, "Homo sapiens": 0.21, "Arabidopsis thaliana": 0.35, "Procambarus clarkii": 0.17, "Caenorhabditis elegans": 0.29, "Aliivibrio fischeri": 0.14, "Pyrocystis fusiformis": 0.08, "Drosophila melanogaster": 0.09, "Physcomitrella patens": 0.17, "Synechocystis sp. PCC 6803": 0.09, "Deinococcus radiodurans R1": 0.02, "Danio rerio": 0.26, "Oryza sativa": 0.15, "Populus trichocarpa": 0.35, "Haloferax volcanii": 0.02, "Hydra vulgaris": 0.41, "Vibrio natriegens": 0.10 },
	"agg": { "aa": "r", "Escherichia coli": 0.07, "Saccaromyces cerevisiae": 0.21, "Bacillus subtilis": 0.10, "Homo sapiens": 0.21, "Arabidopsis thaliana": 0.20, "Procambarus clarkii": 0.18, "Caenorhabditis elegans": 0.08, "Aliivibrio fischeri": 0.02, "Pyrocystis fusiformis": 0.04, "Drosophila melanogaster": 0.11, "Physcomitrella patens": 0.19, "Synechocystis sp. PCC 6803": 0.10, "Deinococcus radiodurans R1": 0.03, "Danio rerio": 0.19, "Oryza sativa": 0.23, "Populus trichocarpa": 0.23, "Haloferax volcanii": 0.01, "Hydra vulgaris": 0.08, "Vibrio natriegens": 0.03 },
	"agc": { "aa": "s", "Escherichia coli": 0.20, "Saccaromyces cerevisiae": 0.11, "Bacillus subtilis": 0.23, "Homo sapiens": 0.24, "Arabidopsis thaliana": 0.13, "Procambarus clarkii": 0.14, "Caenorhabditis elegans": 0.10, "Aliivibrio fischeri": 0.13, "Pyrocystis fusiformis": 0.20, "Drosophila melanogaster": 0.25, "Physcomitrella patens": 0.18, "Synechocystis sp. PCC 6803": 0.18, "Deinococcus radiodurans R1": 0.46, "Danio rerio": 0.22, "Oryza sativa": 0.20, "Populus trichocarpa": 0.14, "Haloferax volcanii": 0.20, "Hydra vulgaris": 0.09, "Vibrio natriegens": 0.19 },
	"agt": { "aa": "s", "Escherichia coli": 0.18, "Saccaromyces cerevisiae": 0.16, "Bacillus subtilis": 0.11, "Homo sapiens": 0.15, "Arabidopsis thaliana": 0.16, "Procambarus clarkii": 0.11, "Caenorhabditis elegans": 0.15, "Aliivibrio fischeri": 0.21, "Pyrocystis fusiformis": 0.04, "Drosophila melanogaster": 0.14, "Physcomitrella patens": 0.14, "Synechocystis sp. PCC 6803": 0.26, "Deinococcus radiodurans R1": 0.09, "Danio rerio": 0.16, "Oryza sativa": 0.11, "Populus trichocarpa": 0.19, "Haloferax volcanii": 0.03, "Hydra vulgaris": 0.23, "Vibrio natriegens": 0.18 },
	"aca": { "aa": "t", "Escherichia coli": 0.25, "Saccaromyces cerevisiae": 0.30, "Bacillus subtilis": 0.40, "Homo sapiens": 0.28, "Arabidopsis thaliana": 0.31, "Procambarus clarkii": 0.26, "Caenorhabditis elegans": 0.34, "Aliivibrio fischeri": 0.34, "Pyrocystis fusiformis": 0.24, "Drosophila melanogaster": 0.20, "Physcomitrella patens": 0.24, "Synechocystis sp. PCC 6803": 0.13, "Deinococcus radiodurans R1": 0.04, "Danio rerio": 0.31, "Oryza sativa": 0.24, "Populus trichocarpa": 0.36, "Haloferax volcanii": 0.02, "Hydra vulgaris": 0.41, "Vibrio natriegens": 0.23 },
	"acg": { "aa": "t", "Escherichia coli": 0.22, "Saccaromyces cerevisiae": 0.14, "Bacillus subtilis": 0.27, "Homo sapiens": 0.11, "Arabidopsis thaliana": 0.15, "Procambarus clarkii": 0.12, "Caenorhabditis elegans": 0.15, "Aliivibrio fischeri": 0.17, "Pyrocystis fusiformis": 0.24, "Drosophila melanogaster": 0.26, "Physcomitrella patens": 0.24, "Synechocystis sp. PCC 6803": 0.14, "Deinococcus radiodurans R1": 0.30, "Danio rerio": 0.13, "Oryza sativa": 0.23, "Populus trichocarpa": 0.10, "Haloferax volcanii": 0.50, "Hydra vulgaris": 0.07, "Vibrio natriegens": 0.23 },
	"acc": { "aa": "t", "Escherichia coli": 0.31, "Saccaromyces cerevisiae": 0.22, "Bacillus subtilis": 0.17, "Homo sapiens": 0.36, "Arabidopsis thaliana": 0.20, "Procambarus clarkii": 0.35, "Caenorhabditis elegans": 0.18, "Aliivibrio fischeri": 0.18, "Pyrocystis fusiformis": 0.36, "Drosophila melanogaster": 0.38, "Physcomitrella patens": 0.23, "Synechocystis sp. PCC 6803": 0.48, "Deinococcus radiodurans R1": 0.60, "Danio rerio": 0.29, "Oryza sativa": 0.31, "Populus trichocarpa": 0.20, "Haloferax volcanii": 0.46, "Hydra vulgaris": 0.10, "Vibrio natriegens": 0.27 },
	"act": { "aa": "t", "Escherichia coli": 0.22, "Saccaromyces cerevisiae": 0.35, "Bacillus subtilis": 0.16, "Homo sapiens": 0.25, "Arabidopsis thaliana": 0.34, "Procambarus clarkii": 0.27, "Caenorhabditis elegans": 0.32, "Aliivibrio fischeri": 0.31, "Pyrocystis fusiformis": 0.16, "Drosophila melanogaster": 0.17, "Physcomitrella patens": 0.30, "Synechocystis sp. PCC 6803": 0.25, "Deinococcus radiodurans R1": 0.07, "Danio rerio": 0.26, "Oryza sativa": 0.22, "Populus trichocarpa": 0.34, "Haloferax volcanii": 0.02, "Hydra vulgaris": 0.42, "Vibrio natriegens": 0.27 },
	"ata": { "aa": "i", "Escherichia coli": 0.21, "Saccaromyces cerevisiae": 0.27, "Bacillus subtilis": 0.13, "Homo sapiens": 0.17, "Arabidopsis thaliana": 0.24, "Procambarus clarkii": 0.14, "Caenorhabditis elegans": 0.16, "Aliivibrio fischeri": 0.14, "Pyrocystis fusiformis": 0.03, "Drosophila melanogaster": 0.19, "Physcomitrella patens": 0.16, "Synechocystis sp. PCC 6803": 0.08, "Deinococcus radiodurans R1": 0.03, "Danio rerio": 0.16, "Oryza sativa": 0.21, "Populus trichocarpa": 0.25, "Haloferax volcanii": 0.03, "Hydra vulgaris": 0.34, "Vibrio natriegens": 0.11 },
	"atg": { "aa": "m", "Escherichia coli": 1.00, "Saccaromyces cerevisiae": 1.00, "Bacillus subtilis": 1.00, "Homo sapiens": 1.00, "Arabidopsis thaliana": 1.00, "Procambarus clarkii": 1.00, "Caenorhabditis elegans": 1.00, "Aliivibrio fischeri": 1.00, "Pyrocystis fusiformis": 1.00, "Drosophila melanogaster": 1.00, "Physcomitrella patens": 1.00, "Synechocystis sp. PCC 6803": 1.00, "Deinococcus radiodurans R1": 1.00, "Danio rerio": 1.00, "Oryza sativa": 1.00, "Populus trichocarpa": 1.00, "Haloferax volcanii": 1.00, "Hydra vulgaris": 1.00, "Vibrio natriegens": 1.00 },
	"atc": { "aa": "i", "Escherichia coli": 0.31, "Saccaromyces cerevisiae": 0.26, "Bacillus subtilis": 0.37, "Homo sapiens": 0.47, "Arabidopsis thaliana": 0.35, "Procambarus clarkii": 0.50, "Caenorhabditis elegans": 0.31, "Aliivibrio fischeri": 0.27, "Pyrocystis fusiformis": 0.67, "Drosophila melanogaster": 0.47, "Physcomitrella patens": 0.43, "Synechocystis sp. PCC 6803": 0.28, "Deinococcus radiodurans R1": 0.67, "Danio rerio": 0.50, "Oryza sativa": 0.46, "Populus trichocarpa": 0.26, "Haloferax volcanii": 0.83, "Hydra vulgaris": 0.11, "Vibrio natriegens": 0.41 },
	"att": { "aa": "i", "Escherichia coli": 0.47, "Saccaromyces cerevisiae": 0.46, "Bacillus subtilis": 0.49, "Homo sapiens": 0.36, "Arabidopsis thaliana": 0.41, "Procambarus clarkii": 0.36, "Caenorhabditis elegans": 0.53, "Aliivibrio fischeri": 0.60, "Pyrocystis fusiformis": 0.31, "Drosophila melanogaster": 0.34, "Physcomitrella patens": 0.41, "Synechocystis sp. PCC 6803": 0.64, "Deinococcus radiodurans R1": 0.31, "Danio rerio": 0.34, "Oryza sativa": 0.33, "Populus trichocarpa": 0.49, "Haloferax volcanii": 0.14, "Hydra vulgaris": 0.55, "Vibrio natriegens": 0.48 },
	"gaa": { "aa": "e", "Escherichia coli": 0.64, "Saccaromyces cerevisiae": 0.70, "Bacillus subtilis": 0.68, "Homo sapiens": 0.42, "Arabidopsis thaliana": 0.52, "Procambarus clarkii": 0.48, "Caenorhabditis elegans": 0.62, "Aliivibrio fischeri": 0.72, "Pyrocystis fusiformis": 0.16, "Drosophila melanogaster": 0.33, "Physcomitrella patens": 0.39, "Synechocystis sp. PCC 6803": 0.74, "Deinococcus radiodurans R1": 0.44, "Danio rerio": 0.36, "Oryza sativa": 0.36, "Populus trichocarpa": 0.55, "Haloferax volcanii": 0.28, "Hydra vulgaris": 0.78, "Vibrio natriegens": 0.65 },
	"gag": { "aa": "e", "Escherichia coli": 0.36, "Saccaromyces cerevisiae": 0.30, "Bacillus subtilis": 0.32, "Homo sapiens": 0.58, "Arabidopsis thaliana": 0.48, "Procambarus clarkii": 0.52, "Caenorhabditis elegans": 0.38, "Aliivibrio fischeri": 0.28, "Pyrocystis fusiformis": 0.84, "Drosophila melanogaster": 0.67, "Physcomitrella patens": 0.61, "Synechocystis sp. PCC 6803": 0.26, "Deinococcus radiodurans R1": 0.56, "Danio rerio": 0.64, "Oryza sativa": 0.64, "Populus trichocarpa": 0.45, "Haloferax volcanii": 0.72, "Hydra vulgaris": 0.22, "Vibrio natriegens": 0.35 },
	"gac": { "aa": "d", "Escherichia coli": 0.35, "Saccaromyces cerevisiae": 0.35, "Bacillus subtilis": 0.36, "Homo sapiens": 0.54, "Arabidopsis thaliana": 0.32, "Procambarus clarkii": 0.61, "Caenorhabditis elegans": 0.32, "Aliivibrio fischeri": 0.21, "Pyrocystis fusiformis": 0.61, "Drosophila melanogaster": 0.47, "Physcomitrella patens": 0.47, "Synechocystis sp. PCC 6803": 0.35, "Deinococcus radiodurans R1": 0.89, "Danio rerio": 0.53, "Oryza sativa": 0.53, "Populus trichocarpa": 0.26, "Haloferax volcanii": 0.97, "Hydra vulgaris": 0.23, "Vibrio natriegens": 0.39 },
	"gat": { "aa": "d", "Escherichia coli": 0.65, "Saccaromyces cerevisiae": 0.65, "Bacillus subtilis": 0.64, "Homo sapiens": 0.46, "Arabidopsis thaliana": 0.68, "Procambarus clarkii": 0.39, "Caenorhabditis elegans": 0.68, "Aliivibrio fischeri": 0.79, "Pyrocystis fusiformis": 0.39, "Drosophila melanogaster": 0.53, "Physcomitrella patens": 0.53, "Synechocystis sp. PCC 6803": 0.65, "Deinococcus radiodurans R1": 0.11, "Danio rerio": 0.47, "Oryza sativa": 0.47, "Populus trichocarpa": 0.74, "Haloferax volcanii": 0.03, "Hydra vulgaris": 0.77, "Vibrio natriegens": 0.61 },
	"gga": { "aa": "g", "Escherichia coli": 0.19, "Saccaromyces cerevisiae": 0.22, "Bacillus subtilis": 0.31, "Homo sapiens": 0.25, "Arabidopsis thaliana": 0.37, "Procambarus clarkii": 0.22, "Caenorhabditis elegans": 0.59, "Aliivibrio fischeri": 0.16, "Pyrocystis fusiformis": 0.04, "Drosophila melanogaster": 0.29, "Physcomitrella patens": 0.30, "Synechocystis sp. PCC 6803": 0.18, "Deinococcus radiodurans R1": 0.06, "Danio rerio": 0.34, "Oryza sativa": 0.21, "Populus trichocarpa": 0.36, "Haloferax volcanii": 0.06, "Hydra vulgaris": 0.41, "Vibrio natriegens": 0.12 },
	"ggg": { "aa": "g", "Escherichia coli": 0.18, "Saccaromyces cerevisiae": 0.12, "Bacillus subtilis": 0.16, "Homo sapiens": 0.25, "Arabidopsis thaliana": 0.16, "Procambarus clarkii": 0.11, "Caenorhabditis elegans": 0.08, "Aliivibrio fischeri": 0.10, "Pyrocystis fusiformis": 0.13, "Drosophila melanogaster": 0.07, "Physcomitrella patens": 0.21, "Synechocystis sp. PCC 6803": 0.24, "Deinococcus radiodurans R1": 0.23, "Danio rerio": 0.16, "Oryza sativa": 0.22, "Populus trichocarpa": 0.19, "Haloferax volcanii": 0.16, "Hydra vulgaris": 0.08, "Vibrio natriegens": 0.10 },
	"ggc": { "aa": "g", "Escherichia coli": 0.29, "Saccaromyces cerevisiae": 0.19, "Bacillus subtilis": 0.34, "Homo sapiens": 0.34, "Arabidopsis thaliana": 0.14, "Procambarus clarkii": 0.42, "Caenorhabditis elegans": 0.12, "Aliivibrio fischeri": 0.21, "Pyrocystis fusiformis": 0.48, "Drosophila melanogaster": 0.43, "Physcomitrella patens": 0.24, "Synechocystis sp. PCC 6803": 0.31, "Deinococcus radiodurans R1": 0.63, "Danio rerio": 0.28, "Oryza sativa": 0.38, "Populus trichocarpa": 0.16, "Haloferax volcanii": 0.69, "Hydra vulgaris": 0.09, "Vibrio natriegens": 0.32 },
	"ggt": { "aa": "g", "Escherichia coli": 0.34, "Saccaromyces cerevisiae": 0.47, "Bacillus subtilis": 0.19, "Homo sapiens": 0.16, "Arabidopsis thaliana": 0.34, "Procambarus clarkii": 0.26, "Caenorhabditis elegans": 0.20, "Aliivibrio fischeri": 0.53, "Pyrocystis fusiformis": 0.35, "Drosophila melanogaster": 0.21, "Physcomitrella patens": 0.25, "Synechocystis sp. PCC 6803": 0.27, "Deinococcus radiodurans R1": 0.08, "Danio rerio": 0.22, "Oryza sativa": 0.19, "Populus trichocarpa": 0.29, "Haloferax volcanii": 0.09, "Hydra vulgaris": 0.42, "Vibrio natriegens": 0.46 },
	"gca": { "aa": "a", "Escherichia coli": 0.27, "Saccaromyces cerevisiae": 0.29, "Bacillus subtilis": 0.28, "Homo sapiens": 0.23, "Arabidopsis thaliana": 0.27, "Procambarus clarkii": 0.20, "Caenorhabditis elegans": 0.31, "Aliivibrio fischeri": 0.37, "Pyrocystis fusiformis": 0.23, "Drosophila melanogaster": 0.17, "Physcomitrella patens": 0.25, "Synechocystis sp. PCC 6803": 0.13, "Deinococcus radiodurans R1": 0.05, "Danio rerio": 0.25, "Oryza sativa": 0.18, "Populus trichocarpa": 0.36, "Haloferax volcanii": 0.04, "Hydra vulgaris": 0.42, "Vibrio natriegens": 0.30 },
	"gcg": { "aa": "a", "Escherichia coli": 0.25, "Saccaromyces cerevisiae": 0.11, "Bacillus subtilis": 0.26, "Homo sapiens": 0.11, "Arabidopsis thaliana": 0.14, "Procambarus clarkii": 0.11, "Caenorhabditis elegans": 0.13, "Aliivibrio fischeri": 0.17, "Pyrocystis fusiformis": 0.20, "Drosophila melanogaster": 0.19, "Physcomitrella patens": 0.22, "Synechocystis sp. PCC 6803": 0.18, "Deinococcus radiodurans R1": 0.38, "Danio rerio": 0.13, "Oryza sativa": 0.28, "Populus trichocarpa": 0.07, "Haloferax volcanii": 0.45, "Hydra vulgaris": 0.05, "Vibrio natriegens": 0.28 },
	"gcc": { "aa": "a", "Escherichia coli": 0.26, "Saccaromyces cerevisiae": 0.22, "Bacillus subtilis": 0.22, "Homo sapiens": 0.40, "Arabidopsis thaliana": 0.16, "Procambarus clarkii": 0.37, "Caenorhabditis elegans": 0.20, "Aliivibrio fischeri": 0.10, "Pyrocystis fusiformis": 0.45, "Drosophila melanogaster": 0.45, "Physcomitrella patens": 0.22, "Synechocystis sp. PCC 6803": 0.45, "Deinococcus radiodurans R1": 0.49, "Danio rerio": 0.30, "Oryza sativa": 0.33, "Populus trichocarpa": 0.18, "Haloferax volcanii": 0.48, "Hydra vulgaris": 0.09, "Vibrio natriegens": 0.16 },
	"gct": { "aa": "a", "Escherichia coli": 0.22, "Saccaromyces cerevisiae": 0.38, "Bacillus subtilis": 0.24, "Homo sapiens": 0.27, "Arabidopsis thaliana": 0.43, "Procambarus clarkii": 0.32, "Caenorhabditis elegans": 0.36, "Aliivibrio fischeri": 0.36, "Pyrocystis fusiformis": 0.12, "Drosophila melanogaster": 0.19, "Physcomitrella patens": 0.31, "Synechocystis sp. PCC 6803": 0.24, "Deinococcus radiodurans R1": 0.08, "Danio rerio": 0.32, "Oryza sativa": 0.21, "Populus trichocarpa": 0.40, "Haloferax volcanii": 0.03, "Hydra vulgaris": 0.44, "Vibrio natriegens": 0.27 },
	"gta": { "aa": "v", "Escherichia coli": 0.19, "Saccaromyces cerevisiae": 0.21, "Bacillus subtilis": 0.20, "Homo sapiens": 0.12, "Arabidopsis thaliana": 0.15, "Procambarus clarkii": 0.13, "Caenorhabditis elegans": 0.16, "Aliivibrio fischeri": 0.29, "Pyrocystis fusiformis": 0.03, "Drosophila melanogaster": 0.11, "Physcomitrella patens": 0.13, "Synechocystis sp. PCC 6803": 0.16, "Deinococcus radiodurans R1": 0.03, "Danio rerio": 0.11, "Oryza sativa": 0.10, "Populus trichocarpa": 0.16, "Haloferax volcanii": 0.01, "Hydra vulgaris": 0.24, "Vibrio natriegens": 0.22 },
	"gtg": { "aa": "v", "Escherichia coli": 0.29, "Saccaromyces cerevisiae": 0.19, "Bacillus subtilis": 0.26, "Homo sapiens": 0.46, "Arabidopsis thaliana": 0.26, "Procambarus clarkii": 0.35, "Caenorhabditis elegans": 0.23, "Aliivibrio fischeri": 0.17, "Pyrocystis fusiformis": 0.36, "Drosophila melanogaster": 0.47, "Physcomitrella patens": 0.43, "Synechocystis sp. PCC 6803": 0.42, "Deinococcus radiodurans R1": 0.62, "Danio rerio": 0.44, "Oryza sativa": 0.36, "Populus trichocarpa": 0.27, "Haloferax volcanii": 0.22, "Hydra vulgaris": 0.12, "Vibrio natriegens": 0.25 },
	"gtc": { "aa": "v", "Escherichia coli": 0.19, "Saccaromyces cerevisiae": 0.21, "Bacillus subtilis": 0.26, "Homo sapiens": 0.24, "Arabidopsis thaliana": 0.19, "Procambarus clarkii": 0.28, "Caenorhabditis elegans": 0.22, "Aliivibrio fischeri": 0.09, "Pyrocystis fusiformis": 0.53, "Drosophila melanogaster": 0.24, "Physcomitrella patens": 0.18, "Synechocystis sp. PCC 6803": 0.17, "Deinococcus radiodurans R1": 0.30, "Danio rerio": 0.23, "Oryza sativa": 0.30, "Populus trichocarpa": 0.18, "Haloferax volcanii": 0.73, "Hydra vulgaris": 0.11, "Vibrio natriegens": 0.19 },
	"gtt": { "aa": "v", "Escherichia coli": 0.32, "Saccaromyces cerevisiae": 0.39, "Bacillus subtilis": 0.28, "Homo sapiens": 0.18, "Arabidopsis thaliana": 0.40, "Procambarus clarkii": 0.24, "Caenorhabditis elegans": 0.39, "Aliivibrio fischeri": 0.46, "Pyrocystis fusiformis": 0.09, "Drosophila melanogaster": 0.19, "Physcomitrella patens": 0.25, "Synechocystis sp. PCC 6803": 0.25, "Deinococcus radiodurans R1": 0.05, "Danio rerio": 0.22, "Oryza sativa": 0.23, "Populus trichocarpa": 0.39, "Haloferax volcanii": 0.03, "Hydra vulgaris": 0.53, "Vibrio natriegens": 0.34 },
	"caa": { "aa": "q", "Escherichia coli": 0.35, "Saccaromyces cerevisiae": 0.69, "Bacillus subtilis": 0.52, "Homo sapiens": 0.27, "Arabidopsis thaliana": 0.56, "Procambarus clarkii": 0.34, "Caenorhabditis elegans": 0.66, "Aliivibrio fischeri": 0.80, "Pyrocystis fusiformis": 0.12, "Drosophila melanogaster": 0.30, "Physcomitrella patens": 0.43, "Synechocystis sp. PCC 6803": 0.62, "Deinococcus radiodurans R1": 0.18, "Danio rerio": 0.26, "Oryza sativa": 0.39, "Populus trichocarpa": 0.54, "Haloferax volcanii": 0.14, "Hydra vulgaris": 0.77, "Vibrio natriegens": 0.59 },
	"cag": { "aa": "q", "Escherichia coli": 0.65, "Saccaromyces cerevisiae": 0.31, "Bacillus subtilis": 0.48, "Homo sapiens": 0.73, "Arabidopsis thaliana": 0.44, "Procambarus clarkii": 0.66, "Caenorhabditis elegans": 0.34, "Aliivibrio fischeri": 0.20, "Pyrocystis fusiformis": 0.88, "Drosophila melanogaster": 0.70, "Physcomitrella patens": 0.57, "Synechocystis sp. PCC 6803": 0.38, "Deinococcus radiodurans R1": 0.82, "Danio rerio": 0.74, "Oryza sativa": 0.61, "Populus trichocarpa": 0.46, "Haloferax volcanii": 0.86, "Hydra vulgaris": 0.23, "Vibrio natriegens": 0.41 },
	"cac": { "aa": "h", "Escherichia coli": 0.37, "Saccaromyces cerevisiae": 0.36, "Bacillus subtilis": 0.32, "Homo sapiens": 0.58, "Arabidopsis thaliana": 0.39, "Procambarus clarkii": 0.67, "Caenorhabditis elegans": 0.39, "Aliivibrio fischeri": 0.36, "Pyrocystis fusiformis": 0.58, "Drosophila melanogaster": 0.60, "Physcomitrella patens": 0.51, "Synechocystis sp. PCC 6803": 0.38, "Deinococcus radiodurans R1": 0.83, "Danio rerio": 0.58, "Oryza sativa": 0.55, "Populus trichocarpa": 0.34, "Haloferax volcanii": 0.96, "Hydra vulgaris": 0.30, "Vibrio natriegens": 0.50 },
	"cat": { "aa": "h", "Escherichia coli": 0.63, "Saccaromyces cerevisiae": 0.64, "Bacillus subtilis": 0.68, "Homo sapiens": 0.42, "Arabidopsis thaliana": 0.61, "Procambarus clarkii": 0.33, "Caenorhabditis elegans": 0.61, "Aliivibrio fischeri": 0.64, "Pyrocystis fusiformis": 0.42, "Drosophila melanogaster": 0.40, "Physcomitrella patens": 0.49, "Synechocystis sp. PCC 6803": 0.62, "Deinococcus radiodurans R1": 0.17, "Danio rerio": 0.42, "Oryza sativa": 0.45, "Populus trichocarpa": 0.66, "Haloferax volcanii": 0.04, "Hydra vulgaris": 0.70, "Vibrio natriegens": 0.50 },
	"cga": { "aa": "r", "Escherichia coli": 0.09, "Saccaromyces cerevisiae": 0.07, "Bacillus subtilis": 0.10, "Homo sapiens": 0.11, "Arabidopsis thaliana": 0.12, "Procambarus clarkii": 0.11, "Caenorhabditis elegans": 0.23, "Aliivibrio fischeri": 0.16, "Pyrocystis fusiformis": 0.10, "Drosophila melanogaster": 0.15, "Physcomitrella patens": 0.17, "Synechocystis sp. PCC 6803": 0.11, "Deinococcus radiodurans R1": 0.03, "Danio rerio": 0.12, "Oryza sativa": 0.09, "Populus trichocarpa": 0.10, "Haloferax volcanii": 0.08, "Hydra vulgaris": 0.18, "Vibrio natriegens": 0.15 },
	"cgg": { "aa": "r", "Escherichia coli": 0.15, "Saccaromyces cerevisiae": 0.04, "Bacillus subtilis": 0.17, "Homo sapiens": 0.20, "Arabidopsis thaliana": 0.09, "Procambarus clarkii": 0.10, "Caenorhabditis elegans": 0.09, "Aliivibrio fischeri": 0.01, "Pyrocystis fusiformis": 0.17, "Drosophila melanogaster": 0.15, "Physcomitrella patens": 0.17, "Synechocystis sp. PCC 6803": 0.26, "Deinococcus radiodurans R1": 0.28, "Danio rerio": 0.12, "Oryza sativa": 0.19, "Populus trichocarpa": 0.10, "Haloferax volcanii": 0.23, "Hydra vulgaris": 0.04, "Vibrio natriegens": 0.03 },
	"cgc": { "aa": "r", "Escherichia coli": 0.26, "Saccaromyces cerevisiae": 0.06, "Bacillus subtilis": 0.20, "Homo sapiens": 0.18, "Arabidopsis thaliana": 0.07, "Procambarus clarkii": 0.25, "Caenorhabditis elegans": 0.10, "Aliivibrio fischeri": 0.15, "Pyrocystis fusiformis": 0.44, "Drosophila melanogaster": 0.33, "Physcomitrella patens": 0.15, "Synechocystis sp. PCC 6803": 0.24, "Deinococcus radiodurans R1": 0.55, "Danio rerio": 0.18, "Oryza sativa": 0.23, "Populus trichocarpa": 0.08, "Haloferax volcanii": 0.62, "Hydra vulgaris": 0.08, "Vibrio natriegens": 0.26 },
	"cgt": { "aa": "r", "Escherichia coli": 0.30, "Saccaromyces cerevisiae": 0.14, "Bacillus subtilis": 0.18, "Homo sapiens": 0.08, "Arabidopsis thaliana": 0.17, "Procambarus clarkii": 0.19, "Caenorhabditis elegans": 0.21, "Aliivibrio fischeri": 0.51, "Pyrocystis fusiformis": 0.17, "Drosophila melanogaster": 0.16, "Physcomitrella patens": 0.14, "Synechocystis sp. PCC 6803": 0.20, "Deinococcus radiodurans R1": 0.09, "Danio rerio": 0.13, "Oryza sativa": 0.10, "Populus trichocarpa": 0.13, "Haloferax volcanii": 0.04, "Hydra vulgaris": 0.22, "Vibrio natriegens": 0.42 },
	"cca": { "aa": "p", "Escherichia coli": 0.23, "Saccaromyces cerevisiae": 0.42, "Bacillus subtilis": 0.19, "Homo sapiens": 0.28, "Arabidopsis thaliana": 0.33, "Procambarus clarkii": 0.31, "Caenorhabditis elegans": 0.53, "Aliivibrio fischeri": 0.45, "Pyrocystis fusiformis": 0.19, "Drosophila melanogaster": 0.25, "Physcomitrella patens": 0.25, "Synechocystis sp. PCC 6803": 0.16, "Deinococcus radiodurans R1": 0.05, "Danio rerio": 0.30, "Oryza sativa": 0.25, "Populus trichocarpa": 0.40, "Haloferax volcanii": 0.02, "Hydra vulgaris": 0.47, "Vibrio natriegens": 0.39 },
	"ccg": { "aa": "p", "Escherichia coli": 0.37, "Saccaromyces cerevisiae": 0.12, "Bacillus subtilis": 0.44, "Homo sapiens": 0.11, "Arabidopsis thaliana": 0.18, "Procambarus clarkii": 0.11, "Caenorhabditis elegans": 0.20, "Aliivibrio fischeri": 0.10, "Pyrocystis fusiformis": 0.19, "Drosophila melanogaster": 0.29, "Physcomitrella patens": 0.20, "Synechocystis sp. PCC 6803": 0.16, "Deinococcus radiodurans R1": 0.41, "Danio rerio": 0.15, "Oryza sativa": 0.31, "Populus trichocarpa": 0.10, "Haloferax volcanii": 0.52, "Hydra vulgaris": 0.06, "Vibrio natriegens": 0.22 },
	"ccc": { "aa": "p", "Escherichia coli": 0.16, "Saccaromyces cerevisiae": 0.15, "Bacillus subtilis": 0.09, "Homo sapiens": 0.32, "Arabidopsis thaliana": 0.11, "Procambarus clarkii": 0.26, "Caenorhabditis elegans": 0.09, "Aliivibrio fischeri": 0.04, "Pyrocystis fusiformis": 0.37, "Drosophila melanogaster": 0.33, "Physcomitrella patens": 0.23, "Synechocystis sp. PCC 6803": 0.48, "Deinococcus radiodurans R1": 0.45, "Danio rerio": 0.24, "Oryza sativa": 0.21, "Populus trichocarpa": 0.12, "Haloferax volcanii": 0.45, "Hydra vulgaris": 0.06, "Vibrio natriegens": 0.07 },
	"cct": { "aa": "p", "Escherichia coli": 0.24, "Saccaromyces cerevisiae": 0.31, "Bacillus subtilis": 0.28, "Homo sapiens": 0.29, "Arabidopsis thaliana": 0.38, "Procambarus clarkii": 0.31, "Caenorhabditis elegans": 0.18, "Aliivibrio fischeri": 0.41, "Pyrocystis fusiformis": 0.25, "Drosophila melanogaster": 0.13, "Physcomitrella patens": 0.32, "Synechocystis sp. PCC 6803": 0.20, "Deinococcus radiodurans R1": 0.09, "Danio rerio": 0.31, "Oryza sativa": 0.23, "Populus trichocarpa": 0.38, "Haloferax volcanii": 0.01, "Hydra vulgaris": 0.42, "Vibrio natriegens": 0.31 },
	"cta": { "aa": "l", "Escherichia coli": 0.06, "Saccaromyces cerevisiae": 0.14, "Bacillus subtilis": 0.05, "Homo sapiens": 0.07, "Arabidopsis thaliana": 0.11, "Procambarus clarkii": 0.08, "Caenorhabditis elegans": 0.09, "Aliivibrio fischeri": 0.14, "Pyrocystis fusiformis": 0.01, "Drosophila melanogaster": 0.09, "Physcomitrella patens": 0.08, "Synechocystis sp. PCC 6803": 0.12, "Deinococcus radiodurans R1": 0.01, "Danio rerio": 0.07, "Oryza sativa": 0.09, "Populus trichocarpa": 0.11, "Haloferax volcanii": 0.01, "Hydra vulgaris": 0.10, "Vibrio natriegens": 0.13 },
	"ctg": { "aa": "l", "Escherichia coli": 0.38, "Saccaromyces cerevisiae": 0.11, "Bacillus subtilis": 0.24, "Homo sapiens": 0.40, "Arabidopsis thaliana": 0.11, "Procambarus clarkii": 0.31, "Caenorhabditis elegans": 0.14, "Aliivibrio fischeri": 0.07, "Pyrocystis fusiformis": 0.33, "Drosophila melanogaster": 0.43, "Physcomitrella patens": 0.24, "Synechocystis sp. PCC 6803": 0.18, "Deinococcus radiodurans R1": 0.58, "Danio rerio": 0.41, "Oryza sativa": 0.23, "Populus trichocarpa": 0.13, "Haloferax volcanii": 0.23, "Hydra vulgaris": 0.07, "Vibrio natriegens": 0.22 },
	"ctc": { "aa": "l", "Escherichia coli": 0.10, "Saccaromyces cerevisiae": 0.06, "Bacillus subtilis": 0.11, "Homo sapiens": 0.20, "Arabidopsis thaliana": 0.17, "Procambarus clarkii": 0.23, "Caenorhabditis elegans": 0.17, "Aliivibrio fischeri": 0.04, "Pyrocystis fusiformis": 0.20, "Drosophila melanogaster": 0.15, "Physcomitrella patens": 0.15, "Synechocystis sp. PCC 6803": 0.12, "Deinococcus radiodurans R1": 0.29, "Danio rerio": 0.18, "Oryza sativa": 0.29, "Populus trichocarpa": 0.13, "Haloferax volcanii": 0.69, "Hydra vulgaris": 0.05, "Vibrio natriegens": 0.09 },
	"ctt": { "aa": "l", "Escherichia coli": 0.15, "Saccaromyces cerevisiae": 0.13, "Bacillus subtilis": 0.23, "Homo sapiens": 0.13, "Arabidopsis thaliana": 0.26, "Procambarus clarkii": 0.18, "Caenorhabditis elegans": 0.25, "Aliivibrio fischeri": 0.20, "Pyrocystis fusiformis": 0.23, "Drosophila melanogaster": 0.10, "Physcomitrella patens": 0.18, "Synechocystis sp. PCC 6803": 0.09, "Deinococcus radiodurans R1": 0.05, "Danio rerio": 0.14, "Oryza sativa": 0.17, "Populus trichocarpa": 0.26, "Haloferax volcanii": 0.04, "Hydra vulgaris": 0.23, "Vibrio natriegens": 0.18 },
	"taa": { "aa": "*", "Escherichia coli": 0.58, "Saccaromyces cerevisiae": 0.48, "Bacillus subtilis": 0.61, "Homo sapiens": 0.30, "Arabidopsis thaliana": 0.36, "Procambarus clarkii": 0.51, "Caenorhabditis elegans": 0.43, "Aliivibrio fischeri": 0.75, "Pyrocystis fusiformis": 0.00, "Drosophila melanogaster": 0.41, "Physcomitrella patens": 0.27, "Synechocystis sp. PCC 6803": 0.44, "Deinococcus radiodurans R1": 0.26, "Danio rerio": 0.36, "Oryza sativa": 0.24, "Populus trichocarpa": 0.30, "Haloferax volcanii": 0.29, "Hydra vulgaris": 0.63, "Vibrio natriegens": 0.66 },
	"tag": { "aa": "*", "Escherichia coli": 0.09, "Saccaromyces cerevisiae": 0.22, "Bacillus subtilis": 0.15, "Homo sapiens": 0.24, "Arabidopsis thaliana": 0.20, "Procambarus clarkii": 0.19, "Caenorhabditis elegans": 0.18, "Aliivibrio fischeri": 0.15, "Pyrocystis fusiformis": 0.00, "Drosophila melanogaster": 0.33, "Physcomitrella patens": 0.37, "Synechocystis sp. PCC 6803": 0.35, "Deinococcus radiodurans R1": 0.10, "Danio rerio": 0.18, "Oryza sativa": 0.31, "Populus trichocarpa": 0.25, "Haloferax volcanii": 0.17, "Hydra vulgaris": 0.18, "Vibrio natriegens": 0.19 },
	"tac": { "aa": "y", "Escherichia coli": 0.35, "Saccaromyces cerevisiae": 0.44, "Bacillus subtilis": 0.35, "Homo sapiens": 0.56, "Arabidopsis thaliana": 0.48, "Procambarus clarkii": 0.67, "Caenorhabditis elegans": 0.44, "Aliivibrio fischeri": 0.37, "Pyrocystis fusiformis": 0.71, "Drosophila melanogaster": 0.63, "Physcomitrella patens": 0.62, "Synechocystis sp. PCC 6803": 0.41, "Deinococcus radiodurans R1": 0.83, "Danio rerio": 0.57, "Oryza sativa": 0.60, "Populus trichocarpa": 0.37, "Haloferax volcanii": 0.95, "Hydra vulgaris": 0.31, "Vibrio natriegens": 0.56 },
	"tat": { "aa": "y", "Escherichia coli": 0.65, "Saccaromyces cerevisiae": 0.56, "Bacillus subtilis": 0.65, "Homo sapiens": 0.44, "Arabidopsis thaliana": 0.52, "Procambarus clarkii": 0.33, "Caenorhabditis elegans": 0.56, "Aliivibrio fischeri": 0.63, "Pyrocystis fusiformis": 0.29, "Drosophila melanogaster": 0.37, "Physcomitrella patens": 0.38, "Synechocystis sp. PCC 6803": 0.59, "Deinococcus radiodurans R1": 0.17, "Danio rerio": 0.43, "Oryza sativa": 0.40, "Populus trichocarpa": 0.63, "Haloferax volcanii": 0.05, "Hydra vulgaris": 0.69, "Vibrio natriegens": 0.44 },
	"tga": { "aa": "*", "Escherichia coli": 0.33, "Saccaromyces cerevisiae": 0.30, "Bacillus subtilis": 0.24, "Homo sapiens": 0.47, "Arabidopsis thaliana": 0.44, "Procambarus clarkii": 0.30, "Caenorhabditis elegans": 0.39, "Aliivibrio fischeri": 0.10, "Pyrocystis fusiformis": 1.00, "Drosophila melanogaster": 0.25, "Physcomitrella patens": 0.36, "Synechocystis sp. PCC 6803": 0.21, "Deinococcus radiodurans R1": 0.64, "Danio rerio": 0.46, "Oryza sativa": 0.45, "Populus trichocarpa": 0.45, "Haloferax volcanii": 0.54, "Hydra vulgaris": 0.18, "Vibrio natriegens": 0.15 },
	"tgg": { "aa": "w", "Escherichia coli": 1.00, "Saccaromyces cerevisiae": 1.00, "Bacillus subtilis": 1.00, "Homo sapiens": 1.00, "Arabidopsis thaliana": 1.00, "Procambarus clarkii": 1.00, "Caenorhabditis elegans": 1.00, "Aliivibrio fischeri": 1.00, "Pyrocystis fusiformis": 1.00, "Drosophila melanogaster": 1.00, "Physcomitrella patens": 1.00, "Synechocystis sp. PCC 6803": 1.00, "Deinococcus radiodurans R1": 1.00, "Danio rerio": 1.00, "Oryza sativa": 1.00, "Populus trichocarpa": 1.00, "Haloferax volcanii": 1.00, "Hydra vulgaris": 1.00, "Vibrio natriegens": 1.00 },
	"tgc": { "aa": "c", "Escherichia coli": 0.48, "Saccaromyces cerevisiae": 0.37, "Bacillus subtilis": 0.54, "Homo sapiens": 0.54, "Arabidopsis thaliana": 0.40, "Procambarus clarkii": 0.58, "Caenorhabditis elegans": 0.45, "Aliivibrio fischeri": 0.26, "Pyrocystis fusiformis": 0.79, "Drosophila melanogaster": 0.71, "Physcomitrella patens": 0.58, "Synechocystis sp. PCC 6803": 0.38, "Deinococcus radiodurans R1": 0.82, "Danio rerio": 0.50, "Oryza sativa": 0.67, "Populus trichocarpa": 0.44, "Haloferax volcanii": 0.61, "Hydra vulgaris": 0.33, "Vibrio natriegens": 0.34 },
	"tgt": { "aa": "c", "Escherichia coli": 0.52, "Saccaromyces cerevisiae": 0.63, "Bacillus subtilis": 0.46, "Homo sapiens": 0.46, "Arabidopsis thaliana": 0.60, "Procambarus clarkii": 0.42, "Caenorhabditis elegans": 0.55, "Aliivibrio fischeri": 0.74, "Pyrocystis fusiformis": 0.21, "Drosophila melanogaster": 0.29, "Physcomitrella patens": 0.42, "Synechocystis sp. PCC 6803": 0.62, "Deinococcus radiodurans R1": 0.18, "Danio rerio": 0.50, "Oryza sativa": 0.33, "Populus trichocarpa": 0.56, "Haloferax volcanii": 0.39, "Hydra vulgaris": 0.67, "Vibrio natriegens": 0.66 },
	"tca": { "aa": "s", "Escherichia coli": 0.18, "Saccaromyces cerevisiae": 0.21, "Bacillus subtilis": 0.23, "Homo sapiens": 0.15, "Arabidopsis thaliana": 0.20, "Procambarus clarkii": 0.17, "Caenorhabditis elegans": 0.26, "Aliivibrio fischeri": 0.27, "Pyrocystis fusiformis": 0.11, "Drosophila melanogaster": 0.09, "Physcomitrella patens": 0.15, "Synechocystis sp. PCC 6803": 0.07, "Deinococcus radiodurans R1": 0.04, "Danio rerio": 0.16, "Oryza sativa": 0.16, "Populus trichocarpa": 0.25, "Haloferax volcanii": 0.01, "Hydra vulgaris": 0.27, "Vibrio natriegens": 0.19 },
	"tcg": { "aa": "s", "Escherichia coli": 0.11, "Saccaromyces cerevisiae": 0.10, "Bacillus subtilis": 0.10, "Homo sapiens": 0.05, "Arabidopsis thaliana": 0.10, "Procambarus clarkii": 0.09, "Caenorhabditis elegans": 0.15, "Aliivibrio fischeri": 0.07, "Pyrocystis fusiformis": 0.06, "Drosophila melanogaster": 0.20, "Physcomitrella patens": 0.17, "Synechocystis sp. PCC 6803": 0.07, "Deinococcus radiodurans R1": 0.22, "Danio rerio": 0.07, "Oryza sativa": 0.16, "Populus trichocarpa": 0.06, "Haloferax volcanii": 0.45, "Hydra vulgaris": 0.06, "Vibrio natriegens": 0.12 },
	"tcc": { "aa": "s", "Escherichia coli": 0.14, "Saccaromyces cerevisiae": 0.16, "Bacillus subtilis": 0.13, "Homo sapiens": 0.22, "Arabidopsis thaliana": 0.13, "Procambarus clarkii": 0.24, "Caenorhabditis elegans": 0.13, "Aliivibrio fischeri": 0.04, "Pyrocystis fusiformis": 0.43, "Drosophila melanogaster": 0.24, "Physcomitrella patens": 0.16, "Synechocystis sp. PCC 6803": 0.27, "Deinococcus radiodurans R1": 0.15, "Danio rerio": 0.18, "Oryza sativa": 0.21, "Populus trichocarpa": 0.11, "Haloferax volcanii": 0.28, "Hydra vulgaris": 0.05, "Vibrio natriegens": 0.08 },
	"tct": { "aa": "s", "Escherichia coli": 0.18, "Saccaromyces cerevisiae": 0.26, "Bacillus subtilis": 0.20, "Homo sapiens": 0.19, "Arabidopsis thaliana": 0.28, "Procambarus clarkii": 0.25, "Caenorhabditis elegans": 0.21, "Aliivibrio fischeri": 0.28, "Pyrocystis fusiformis": 0.17, "Drosophila melanogaster": 0.08, "Physcomitrella patens": 0.20, "Synechocystis sp. PCC 6803": 0.15, "Deinococcus radiodurans R1": 0.05, "Danio rerio": 0.20, "Oryza sativa": 0.16, "Populus trichocarpa": 0.26, "Haloferax volcanii": 0.03, "Hydra vulgaris": 0.29, "Vibrio natriegens": 0.24 },
	"tta": { "aa": "l", "Escherichia coli": 0.18, "Saccaromyces cerevisiae": 0.28, "Bacillus subtilis": 0.21, "Homo sapiens": 0.08, "Arabidopsis thaliana": 0.14, "Procambarus clarkii": 0.06, "Caenorhabditis elegans": 0.11, "Aliivibrio fischeri": 0.43, "Pyrocystis fusiformis": 0.03, "Drosophila melanogaster": 0.05, "Physcomitrella patens": 0.09, "Synechocystis sp. PCC 6803": 0.23, "Deinococcus radiodurans R1": 0.01, "Danio rerio": 0.07, "Oryza sativa": 0.07, "Populus trichocarpa": 0.13, "Haloferax volcanii": 0.00, "Hydra vulgaris": 0.37, "Vibrio natriegens": 0.20 },
	"ttg": { "aa": "l", "Escherichia coli": 0.13, "Saccaromyces cerevisiae": 0.29, "Bacillus subtilis": 0.16, "Homo sapiens": 0.13, "Arabidopsis thaliana": 0.22, "Procambarus clarkii": 0.14, "Caenorhabditis elegans": 0.23, "Aliivibrio fischeri": 0.12, "Pyrocystis fusiformis": 0.19, "Drosophila melanogaster": 0.18, "Physcomitrella patens": 0.26, "Synechocystis sp. PCC 6803": 0.26, "Deinococcus radiodurans R1": 0.07, "Danio rerio": 0.13, "Oryza sativa": 0.16, "Populus trichocarpa": 0.23, "Haloferax volcanii": 0.03, "Hydra vulgaris": 0.18, "Vibrio natriegens": 0.18 },
	"ttc": { "aa": "f", "Escherichia coli": 0.36, "Saccaromyces cerevisiae": 0.41, "Bacillus subtilis": 0.32, "Homo sapiens": 0.54, "Arabidopsis thaliana": 0.49, "Procambarus clarkii": 0.72, "Caenorhabditis elegans": 0.51, "Aliivibrio fischeri": 0.28, "Pyrocystis fusiformis": 0.74, "Drosophila melanogaster": 0.62, "Physcomitrella patens": 0.58, "Synechocystis sp. PCC 6803": 0.26, "Deinococcus radiodurans R1": 0.66, "Danio rerio": 0.53, "Oryza sativa": 0.63, "Populus trichocarpa": 0.40, "Haloferax volcanii": 0.94, "Hydra vulgaris": 0.17, "Vibrio natriegens": 0.41 },
	"ttt": { "aa": "f", "Escherichia coli": 0.64, "Saccaromyces cerevisiae": 0.59, "Bacillus subtilis": 0.68, "Homo sapiens": 0.46, "Arabidopsis thaliana": 0.51, "Procambarus clarkii": 0.28, "Caenorhabditis elegans": 0.49, "Aliivibrio fischeri": 0.72, "Pyrocystis fusiformis": 0.26, "Drosophila melanogaster": 0.38, "Physcomitrella patens": 0.42, "Synechocystis sp. PCC 6803": 0.74, "Deinococcus radiodurans R1": 0.34, "Danio rerio": 0.47, "Oryza sativa": 0.37, "Populus trichocarpa": 0.60, "Haloferax volcanii": 0.06, "Hydra vulgaris": 0.83, "Vibrio natriegens": 0.59 }
	}

aa_prefs = {}

gfp_aa_seq = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK*"
### The following is a sequence that almost doubles the optimizer output for a random seed of 42.
### Normal GFP will sometimes almost double when a seed isn't set.
### gfp_aa_seq = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKHNIEDGSVQLADHYQQNTPIGPVLLPDNHYLSTQSALSKDPKRDHMVLLEFVTAAGITHGMDELYK*"

# target_species = { "Saccaromyces cerevisiae": 1, "Procambarus clarkii": 1, "Escherichia coli": 1, "Caenorhabditis elegans": 1, "Aliivibrio fischeri": 1, "Pyrocystis fusiformis": 1, "Vibrio natriegens": 1, "Physcomitrella patens": 1, "Synechocystis sp. PCC 6803": 1, "Deinococcus radiodurans R1": 1, "Danio rerio": 1, "Drosophila melanogaster": 1, "Homo sapiens": 1, "Oryza sativa": 1, "Bacillus subtilis": 1, "Arabidopsis thaliana": 1, "Populus trichocarpa": 1, "Haloferax volcanii": 1, "Hydra vulgaris": 1 }  # all the species
# target_species = { "Escherichia coli": 1, "Saccaromyces cerevisiae": 1 }  # demonstration of how saccaromyces ruins everything
# target_species = { "Arabidopsis thaliana": 1, "Bacillus subtilis": 2, "Escherichia coli": 6, "Saccaromyces cerevisiae": 3, "Synechocystis sp. PCC 6803": 1, "Vibrio natriegens": 1 }  # wishful pDestination fluorescence
target_species = { "Bacillus subtilis": 2, "Escherichia coli": 8, "Saccaromyces cerevisiae": 3, "Synechocystis sp. PCC 6803": 1, "Vibrio natriegens": 1 }  # original optimimzation, actual pDestination fluorescence
# target_species = { "Bacillus subtilis": 1, "Danio rerio": 1, "Escherichia coli": 8, "Saccaromyces cerevisiae": 1, "Vibrio natriegens": 1 }  # pBsaI fluorescence
# target_species = { "Escherichia coli": 3, "Vibrio natriegens": 1 }  # Golden Gate enzymes
target_species = {}  # the weights of the species to optimize for

restriction_enzymes = []  # the restriction enzymes to use

def add_codon_preference(pref_list, label):
	'''
	adds a provided codon preference dictionary to the codon_dict variable
	arguments:
		pref_list = a dictionary containing species-specific condon prefences in the format of { codon: fractional_preference }
		label = what the preference should be labeled as within codon_dict
	'''
	for codon in pref_list.keys():
		lower_codon = codon.lower()
		codon_dict[lower_codon][label] = pref_list[codon]

def freqs_to_fracs(freq_dict):
	'''
	converts codon frequencies into codon fractions
	(converts codon occurrences per 1,000 to a percentage of how often the codon is used to yield its corresponding amino acid)
	accepts dictionaries in the format of { DNA_codon: frequency, ... }
	'''
	# makes sure the frequency dictionary uses lowercase letters
	lower_freq_dict = {}
	for codon in freq_dict:
		if codon != codon.lower():
			lower_freq_dict[codon.lower()] = freq_dict[codon]
	# establishes the total appearance of each amino acid
	aa_totals = {}
	for aa in aa_dict:
		if aa != "o" and aa != "u":
			aa_totals[aa] = 0.0
			for codon in aa_dict[aa]:
				aa_totals[aa] += lower_freq_dict[codon]
	# converts the frequencies to fractions/percentages
	frac_dict = {}
	for codon, frequency in lower_freq_dict.items():
		frac_dict[codon] = frequency / aa_totals[codon_dict[codon]["aa"]]
	return frac_dict

def display_codon_dict():
	'''
	displays the dictionary "codon_dict" which contains the amino acid and species-specific preference for each codon
	'''
	# add_codon_preference(vibrio, "Vibrio natriegens")
	text = ""
	for codon in codon_dict.keys():
		text += '\t"' + codon + '": {'
		for species in codon_dict[codon].keys():
			if isinstance(codon_dict[codon][species], float):  # if adding the species-specific preference
				text += ' "' + species + '": {:.{}f}'.format(codon_dict[codon][species], 2) + ','
			else:  # if adding the designated amino acid
				text += ' "' + species + '": "' + codon_dict[codon][species] + '",'
		text = text[0:-1] + " },\n"
	text = text[0:-2]
	result.replace_text(text)
	
def set_preferences():
	'''
	determines what percentage of the time each codon will be used
	takes into account your species preference
	'''
	global aa_dict, codon_dict, aa_prefs, target_species
	# sets the internal weights for each species
	for box in species_boxes:
		target_species[box.get_label()] = int(box.entry.get() or 0)
	ts = {key: value for key, value in target_species.items() if value != 0}  # removes species with a weight of 0
	print(ts)
	if not ts:  # if no species are selected
		return
	# assigns a weight to each codon
	# averages with preference given to more important species and a penalty given for at least one species having an extra low preference
	for aa in aa_dict:
		if aa == "o" or aa == "u":  # if it's a non-canonical amino acid
			continue  # don't execute the loop this time
		codons = aa_dict[aa]
		aa_prefs[aa] = { "codons": [], "weights": [] }
		for codon in codons:
			aa_prefs[aa]["codons"].append(codon)
			weighted_num_of_species = 0.0
			weight = 0.0
			worst = 1.0  # the worst fraction of preference
			for s in ts:
				weighted_num_of_species += ts[s]
				weight += codon_dict[codon][s] * ts[s]
				if codon_dict[codon][s] < worst:
					worst = codon_dict[codon][s]
			aa_prefs[aa]["weights"].append((weight / weighted_num_of_species + worst * 5) / 6)
	# adjusts codons with low usage
	threshold = 0.11
	one_species = False
	if len(ts.keys()) == 1:  # if optimizing for only one organism
		threshold = 0.08
		one_species = True
	for aa in aa_prefs:
		best_value = [0, 0]  # holds the best value just in case all of the weights are bad  ### likely not needed
		low_proportion = 0.0  # the percentage of the total that the low codons should occupy
		high_sum = 0.0  # the sum of the values above the threshold
		for index, weight in enumerate(aa_prefs[aa]["weights"]):
			if weight > best_value[1]:
				best_value[0] = index
				best_value[1] = weight
			if weight < threshold:  # if the average percentage of preference is below the threshold
				if one_species:
					# excludes rare codons
					low_proportion += 0
					aa_prefs[aa]["weights"][index] = 0  # adjusts the weight
				else:
					# finds the unweighted average preference for the codon
					unweighted_average = 0.0
					for s in codon_dict[aa_prefs[aa]["codons"][index]]:
						if s in ts:
							unweighted_average += codon_dict[aa_prefs[aa]["codons"][index]][s]
					unweighted_average = unweighted_average / len(ts.keys())
					# determines what the best adjustment to the weight would be
					adjusted_preference = 1.0
					for s in codon_dict[aa_prefs[aa]["codons"][index]]:
						if s in ts:
							species_preference = codon_dict[aa_prefs[aa]["codons"][index]][s]
							adjusted_preference = min(  # adjust the preference to the least of:
								species_preference * 1.5,  # 150% of the smallest value (most likely with an outlier)
								unweighted_average,  # the unweighted average (most likely when no species prefers)
								threshold,  # the threshold value (most likely with worst preferences that aren't too bad)
								adjusted_preference  # actually, the preference was already lowest
								)
					low_proportion += adjusted_preference
					aa_prefs[aa]["weights"][index] = adjusted_preference  # adjusts the weight
			else:
				high_sum += weight
		# makes sure the larger preferences are weighted correctly
		for index, weight in enumerate(aa_prefs[aa]["weights"]):
			if weight > threshold:
				aa_prefs[aa]["weights"][index] = weight * (1.0 - low_proportion) / high_sum
		# provides a backup if all of the codons were bad  ### (unused but retained just in case)
		if sum(aa_prefs[aa]["weights"]) == 0:  # if all of the codons were bad
			aa_prefs[aa]["weights"][best_value[0]] = best_value[1]  # use the best available codon

def display_preferences():
	# displays the codon usage
	text = ""
	ts = {key: value for key, value in target_species.items() if value != 0}  # removes species with a weight of 0
	for aa in aa_prefs:
		text += aa + ":\n"
		total = sum(aa_prefs[aa]["weights"])
		for index, codon in enumerate(aa_prefs[aa]["codons"]):
			text += "{} {:.{}f}% (".format(codon, aa_prefs[aa]["weights"][index] / total * 100, 1)
			for s in ts:
				text += s + ": {}%, ".format(int(codon_dict[codon][s] * 100))  # shows individual preferences
			text = text[0:-2] + ")\n"
	result.replace_text(text)

def dna_to_aa(sequence):
	'''
	converts a DNA sequence into an amino acid sequence
	'''
	codons = [sequence[i:i+3] for i in range(0, len(sequence), 3)]  # turns the sequence into an array of 3-character strings
	amino_acids = ""
	for codon in codons:
		if codon.lower() in codon_dict:
			amino_acids += codon_dict[codon.lower()]["aa"]
		else:
			amino_acids += "?"
	return amino_acids

def reverse_complement(dna):
	new_dna = ""
	for letter in dna:
		if letter == "a":
			new_dna += "t"
		elif letter == "c":
			new_dna += "g"
		elif letter == "g":
			new_dna += "c"
		elif letter == "t":
			new_dna += "a"
		else:
			new_dna += "?"
		'''
		### This causes an error for no apparent reason.
		match letter:
			case "a":
				new_dna += "t"
			case "c":
				new_dna += "g"
			case "g":
				new_dna += "c"
			case "t":
				new_dna += "a"
			case "b":
				new_dna += "s"
			case "p":
				new_dna += "z"
			case "s":
				new_dna += "b"
			case "z":
				new_dna += "p"
			case _:
				new_dna += "?"
		'''
	return new_dna[::-1]

def assign_codons(sequence):
	dna = ""
	for aa in sequence:
		if aa in aa_prefs:
			dna += random.choices(aa_prefs[aa]["codons"], weights=aa_prefs[aa]["weights"])[0]
		else:
			print("Bad amino acid: {}".format(aa))
			dna += "???"
	return dna

def find_bad_seqs(seq):
	amount = 0
	rand_sites = []
	cut_sites = []
	# checks for random bad sequences of DNA
	for bad_seq in ["aaaaa", "ttttt", "ggagg", "taaggag"]:  # tries to avoid terminators and strong ribosome binding sites
		occurrences = count_overlapping(seq, bad_seq, return_indices=True)
		amount += occurrences[0] * 5
		for index in occurrences[1]:
			rand_sites.append((index, index + len(bad_seq)))
	# checks for restriction sites
	prs = []  # possible restriction sites
	'''
	restriction_enzymes = [
		"ggatcc",	# BamHI
		"gaagac",	# BbsI # semi-important
		"ggtctc",	# BsaI ## important ##
		"cgtctc",	# BsmBI # semi-important
		"gaattc",	# EcoRI
		"gatatc",	# EcoRV # maybe important
		"aagctt",	# HindIII
		"ggtacc",	# KpnI
		"ccatgg",	# NcoI ## important ##
		"catatg",	# NdeI
		"gcggccgc",	# NotI
		"ctgcag",	# PstI # maybe important
		"gagctc",	# SacI
		"gtcgac",	# SalI
		"gctcttc",	# SapI ## important ##
		"cccggg",	# SmaI # maybe important
		"tctaga",	# XbaI ## important ##
		"ctcgag"	# XhoI
		]
	'''
	for restriction_site in restriction_enzymes:
		prs.append(restriction_site)
		if restriction_site != reverse_complement(restriction_site):  # if the restriction site isn't palindromic
			prs.append(reverse_complement(restriction_site))
	for cut_site in prs:  # tries to avoid restriction enzyme cut sites
		occurrences = count_overlapping(seq, cut_site, return_indices=True)
		amount += occurrences[0] * 10
		for index in occurrences[1]:
			cut_sites.append((index, index + len(cut_site)))
	return amount, rand_sites, cut_sites

def calculate_tm(seq):
	'''
	Uses Wallace's Rule to give a rough estimate on the thermal melting point
	'''
	return float(4 * (seq.count("g") + seq.count("c")) + 2 * (seq.count("a") + seq.count("t")))

def count_hairpins(seq):
	count = 0
	for size in [18, 20, 22, 24]:
		search_size = size
		for i in range(len(seq) - search_size * 2):
			forward = seq[i:i+search_size]
			reverse = reverse_complement(forward)
			search_area = seq[i+search_size:]
			for j in range(len(search_area) - search_size):
				checking_location = search_area[j:j+search_size]
				if float(compare_iterables(reverse, checking_location)) / search_size <= 0.25:  # if the sequence is at least 75% similar
					if calculate_tm(reverse) >= 60 or calculate_tm(checking_location) >= 60:  # if the Tm is >= 60 degees Celsius
						count += 1  # increase the number of hairpins identified
	if (count > 0):
		print("Found hairpin")
	return count

def find_gc_content(seq):
	return float(seq.count("g") + seq.count("c")) / len(seq)

def evaluate_codon_usage(seq):
	# checks for still using reasonable percentages of codons
	penalty = 0
	tolerance = 100  # tolerate values that differ by < 100%
	for codon, info in codon_dict.items():
		aa_info = aa_prefs[info["aa"]]
		num_of_codons = sum(1 for i in range(0, len(seq), 3) if seq[i:i+3] in aa_info["codons"])
		codon_weight = aa_info["weights"][aa_info["codons"].index(codon)]
		expected_num = max(codon_weight * num_of_codons, .000001)
		observed_num = sum(1 for i in range(0, len(seq), 3) if seq[i:i+3] == codon)
		percent_error = abs(expected_num - observed_num) / expected_num
		penalty += math.floor(percent_error * (100 / tolerance))
	return penalty

def align_and_merge(segment_index_list):
	bad_codons = []
	for first, last in segment_index_list:  # makes sure the indices align with codon boundaries
		bad_codons.append((first - first % 3, last + 3 - (3 if last % 3 == 0 else last % 3)))
	segments = []
	start, end = None, None
	for segment in sorted(bad_codons):  # sorted(bad_codons, key=lambda x: x[0])
		if start is None:
			start, end = segment
		elif segment[0] <= end:
			end = max(end, segment[1])
		else:
			segments.append((start, end))
			start, end = segment
	segments.append((start, end))
	return segments

def optimize_amino_acids():
	'''
	turn a string of amino acids or DNA into a species-optimized sequence of DNA
	'''
	global restriction_enzymes
	sequence = ""
	if not aa_input.is_empty():  # if amino acids were provided
		sequence = aa_input.get().strip().lower()
	elif not DNA_input.is_empty():  # if DNA was provided
		sequence = dna_to_aa(DNA_input.get().strip())
	else:  # if no sequence was provided
		messagebox.showerror("Error", "No sequence data was provided.")
		raise ValueError("No sequence data was provided.")
	random.seed(42)  # makes optimizations reproducible
	best_seq = { "seq": "", "score": float("-inf"), "probs": [], "bad_probs": [], "gc": 0, "unsuccessful": 0 }
	restriction_enzymes = []
	for box in restriction_checkbuttons:
		if box.is_selected():
			restriction_enzymes.append(box.seq)
	print(restriction_enzymes)
	for _ in range(80):  # finds the best of 80 random optimization attempts
		p = { "seq": "", "score": 100, "probs": [], "bad_probs": [], "gc": 0 }
		# assigns codons to every amino acid based on the codon preferences
		p["seq"] = assign_codons(sequence)
		# checks for sequence issues
		penalties = find_bad_seqs(p["seq"])
		p["score"] -= penalties[0]
		p["probs"].extend(penalties[1])
		p["bad_probs"].extend(penalties[2])
		# looks for hairpins within the first 50 base pairs
		number_of_hairpins = count_hairpins(p["seq"][0:50])
		if number_of_hairpins > 0:  # if there are any hairpins
			p["score"] -= number_of_hairpins * 5
			p["probs"].append((17, 29))  # sets an arbitrary place to attempt to work out the hairpin(s)
		# checks for reasonable GC content
		gc_content = find_gc_content(p["seq"])
		if gc_content < 0.3:
			p["score"] -= ((.3 - gc_content) * 100) ** 2
		elif gc_content > 0.6:
			p["score"] -= ((gc_content - .6) * 100) ** 2
		p["gc"] = gc_content * 100
		# checks for using reasonable percentages of codons
		p["score"] -= evaluate_codon_usage(p["seq"])
		# assigns the best-scoring sequence
		if p["score"] > best_seq["score"]:
			best_seq["score"] = p["score"]
			best_seq["seq"] = p["seq"]
			best_seq["probs"] = p["probs"]
			best_seq["bad_probs"] = p["bad_probs"]
			best_seq["gc"] = p["gc"]
		# decides whether more attempts should be made
		print(best_seq["score"])
		if best_seq["score"] == 100:  # if the sequence has no problems
			break
	print("-")
	if len(best_seq["probs"] + best_seq["bad_probs"]) > 0:
		# tries correcting issues in a progressive manner
		# finds the problem segments
		segments = align_and_merge(best_seq["probs"] + best_seq["bad_probs"])
		for _ in range(80):  # tries to fix the problems up to 80 times
			p = { "seq": best_seq["seq"], "score": 100, "probs": [], "bad_probs": [], "gc": 0 }
			if best_seq["unsuccessful"] > 0 and random.randint(min(best_seq["unsuccessful"], 25), 25) == 25:  # if the sequence hasn't improved and it's randomly decided to be necessary
				# expands the areas considered to have problems
				temp_probs = []
				for start, end in best_seq["probs"]:
					temp_probs.append((max(start - 3, 0), min(end + 3, len(best_seq["seq"]))))
				best_seq["probs"] = temp_probs
				temp_bad_probs = []
				for start, end in best_seq["bad_probs"]:
					temp_bad_probs.append((max(start - 3, 0), min(end + 3, len(best_seq["seq"]))))
				best_seq["bad_probs"] = temp_bad_probs
				segments = align_and_merge(best_seq["probs"] + best_seq["bad_probs"])
			# reassigns bad segments to new codons
			for pos in segments:
				p["seq"] = p["seq"][0:pos[0]] + assign_codons(dna_to_aa(best_seq["seq"][pos[0]:pos[1]])) + p["seq"][pos[1]:]
			# checks for sequence issues
			penalties = find_bad_seqs(p["seq"])
			p["score"] -= penalties[0]
			p["probs"].extend(penalties[1])
			p["bad_probs"].extend(penalties[2])
			# looks for hairpins within the first 50 base pairs
			number_of_hairpins = count_hairpins(p["seq"][0:50])
			if number_of_hairpins > 0:  # if there are any hairpins
				p["score"] -= number_of_hairpins * 5
				p["probs"].append((17, 29))  # sets an arbitrary place to attempt to work out the hairpin(s)
			# checks for reasonable GC content
			gc_content = find_gc_content(p["seq"])
			if gc_content < 0.3:
				p["score"] -= ((.3 - gc_content) * 100) ** 2
			elif gc_content > 0.6:
				p["score"] -= ((gc_content - .6) * 100) ** 2
			p["gc"] = gc_content * 100
			# checks for still using reasonable percentages of codons
			p["score"] -= evaluate_codon_usage(p["seq"])
			print(best_seq["score"])
			# assigns the best-scoring sequence
			if p["score"] > best_seq["score"]:
				best_seq["score"] = p["score"]
				best_seq["seq"] = p["seq"]
				best_seq["probs"] = p["probs"]
				best_seq["bad_probs"] = p["bad_probs"]
				best_seq["gc"] = p["gc"]
				best_seq["unsuccessful"] = 0
			else:
				best_seq["unsuccessful"] += 1
			# decides whether more attempts should be made
			if best_seq["score"] == 100:  # if the sequence has no problems
				break
	print("Done")
	# displays the sequence and score
	result.replace_text(best_seq["seq"], resize=False)
	optimization_score.replace_text("Score: {}/100".format(best_seq["score"]), resize=True)
	gc_content_display.replace_text("GC content: {:.{}f}%".format(best_seq["gc"], 1), resize=True)
	# color codes the codons based on preference
	for index in range(int(len(best_seq["seq"]) / 3)):
		codon = best_seq["seq"][index*3:index*3+3]
		amino_acid = codon_dict[codon]["aa"]
		codon_index = aa_prefs[amino_acid]["codons"].index(codon)
		preference = aa_prefs[amino_acid]["weights"][codon_index]
		pref_255 = int(min(preference * 4 * 255, 255))
		result.text.tag_config("codon_{}".format(index), foreground="#00{:02}{:02}".format(hex(pref_255)[2:], hex(255-pref_255)[2:]))
		result.text.tag_add("codon_{}".format(index), "1.{}".format(index*3), "1.{}".format(index*3+3))
	# highlights any issues
	result.text.tag_config("issue", foreground="orange")
	result.text.tag_config("bad_issue", foreground="red")
	for start, end in best_seq["probs"]:
		result.text.tag_add("issue", "1.{}".format(start), "1.{}".format(end))
	for start, end in best_seq["bad_probs"]:
		result.text.tag_add("bad_issue", "1.{}".format(start), "1.{}".format(end))
	'''
	# draws attention to important parts of the sequence
	result.text.tag_config("underline", underline=1)
	for site in ["gatatc", "ggtctc"]:
		span = len(site)
		locations = find_overlapping(best_seq["seq"], site)
		if True:  # if the other strand of DNA should be checked
			locations.extend(find_overlapping(best_seq["seq"], reverse_complement(site)))
		for i in locations:
			result.text.tag_add("underline", "1.{}".format(i), "1.{}".format(i+span))
	'''
	# returns the cursor back to nomal
	gui.root.config(cursor="")
	optimize_button.config(cursor="hand2")

def start_optimizing():
	set_preferences()
	# aa_input.delete(0, "end")
	# aa_input.insert(0, gfp_aa_seq.lower())  # provides a default amino acid sequence for testing purposes
	if any(weight > 0 for weight in target_species.values()):  # if at least one species has a weight greater than zero
		if not (DNA_input.is_empty() and aa_input.is_empty()):  # if a sequence was provided
			gui.root.config(cursor="watch")
			optimize_button.config(cursor="watch")
			threading.Thread(target=optimize_amino_acids).start()
		else:
			messagebox.showerror("Error", "No sequence was provided to optimize.")
	else:
		messagebox.showerror("Error", "At least one species must have a weight greater than zero.")

def toggle_species():
	if species_section.winfo_ismapped():
		species_section.pack_forget()
	else:
		species_section.pack(after=checkboxes_frame)

def toggle_enzymes():
	if enzymes_section.winfo_ismapped():
		enzymes_section.pack_forget()
	else:
		enzymes_section.pack(after=checkboxes_frame)

gui = GUI(title="Codon optimizer")
# title
gui.pack_padding(2)
gui.make_text("Codon optimizer", 15).pack()
# theme radiobuttons
theme_buttons = gui.make_frame()
gui.make_radiobutton("theme", "light", "Light theme", parent=theme_buttons, command=lambda: gui.change_theme(preset="light")).grid(row=0, column=0)
gui.make_radiobutton("theme", "dark", "Dark theme", selected=True, parent=theme_buttons, command=lambda: gui.change_theme(preset="dark")).grid(row=0, column=1)
theme_buttons.pack(pady=5)
# shows some help
gui.make_button("Open help on GitHub", command=lambda: webbrowser.open("https://github.com/EpicenterPrograms/codonoptimizer?tab=readme-ov-file#codon-optimizer")).pack(pady=5)
# checkboxes for options
checkboxes_frame = gui.make_frame()
show_species = gui.make_checkbutton("Show species weights", command=toggle_species, parent=checkboxes_frame)
show_species.grid(column=0, row=0)
show_enzymes = gui.make_checkbutton("Show restriction sites", command=toggle_enzymes, parent=checkboxes_frame)
show_enzymes.grid(column=1, row=0)
checkboxes_frame.pack(pady=5)
# species section
species_boxes = []
species_section = gui.make_frame()
for index, name in enumerate([
	"Aliivibrio fischeri",
	"Arabidopsis thaliana",
	"Bacillus subtilis",
	"Caenorhabditis elegans",
	"Danio rerio",
	"Deinococcus radiodurans R1",
	"Drosophila melanogaster",
	"Escherichia coli",
	"Haloferax volcanii",
	"Homo sapiens",
	"Hydra vulgaris",
	"Oryza sativa",
	"Physcomitrella patens",
	"Populus trichocarpa",
	"Procambarus clarkii",
	"Pyrocystis fusiformis",
	"Saccaromyces cerevisiae",
	"Synechocystis sp. PCC 6803",
	"Vibrio natriegens"
	]):
	species_boxes.append(gui.make_labeled_entry(name, parent=species_section, entry_width=3))
	species_boxes[-1].grid(column=index%3, row=index//3, pady=5, sticky="e")  # makes 3 columns aligned to the right
	target_species[name] = 0
for box in species_boxes:
	if box.get_label() == "Escherichia coli":
		box.entry.insert(0, "1")
	else:
		box.entry.insert(0, "0")
# enzymes section
enzymes_section = gui.make_frame()
gui.make_text("Select restriction sites to avoid", 4, parent=enzymes_section).grid(row=0, column=0, columnspan=4, sticky="ew")
enzyme_cuts = {
	"BamHI": "ggatcc",
	"BbsI": "gaagac",
	"BsaI": "ggtctc",
	"BsmBI": "cgtctc",
	"EcoRI": "gaattc",
	"EcoRV": "gatatc",
	"HindIII": "aagctt",
	"KpnI": "ggtacc",
	"NcoI": "ccatgg",
	"NdeI": "catatg",
	"NotI": "gcggccgc",
	"PstI": "ctgcag",
	"SacI": "gagctc",
	"SalI": "gtcgac",
	"SapI": "gctcttc",
	"SmaI": "cccggg",
	"XbaI": "tctaga",
	"XhoI": "ctcgag"
}
restriction_checkbuttons = []
index = 0
for name, site in enzyme_cuts.items():
	checkbox = gui.make_checkbutton("{} ({})".format(name, site.upper()), parent=enzymes_section, selected=False)
	checkbox.seq = site
	checkbox.grid(column=index%4, row=index//4+1, padx=2, pady=2, sticky="w")
	restriction_checkbuttons.append(checkbox)
	index += 1
# allows inputting DNA or amino acids
input_frame = gui.make_frame()
DNA_input = gui.make_entry(placeholder="DNA here", parent=input_frame)
DNA_input.grid(column=0, row=0)
gui.make_text(" or ", 5, parent=input_frame).grid(column=1, row=0)
aa_input = gui.make_entry(placeholder="Amino acids here", parent=input_frame)
aa_input.grid(column=2, row=0)
input_frame.pack(pady=5)
# shows codon preferences or optimization results
buttons_frame = gui.make_frame()
gui.make_button("Show codon\npreferences", lambda: (set_preferences(), display_preferences()), parent=buttons_frame).grid(column=0, row=0, padx=5)
optimize_button = gui.make_button("Optimize", start_optimizing, parent=buttons_frame)
optimize_button.grid(column=1, row=0, padx=5)
buttons_frame.pack(pady=5)
# shows information about the result
info_frame = gui.make_frame()
optimization_score = gui.make_text("Score:", 5, parent=info_frame)
optimization_score.grid(column=0, row=0)
gc_content_display = gui.make_text("GC content:", 5, parent=info_frame)
gc_content_display.grid(column=1, row=0)
info_frame.pack()
# displays the optimized DNA sequence
result = gui.make_text("", 5, width=80, height=12)
result.pack()
# show the window
gui.appear()

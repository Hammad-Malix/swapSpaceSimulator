

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from collections import deque
from typing import List, Tuple, Optional


class PageReplacementAlgorithm:
    """Base class for page replacement algorithms"""
    
    def __init__(self, ram_frames: int, swap_frames: int):
        self.ram_frames = ram_frames
        self.swap_frames = swap_frames
        self.ram = []  # Current pages in RAM
        self.swap_space = []  # Current pages in swap space
        self.page_faults = 0
        self.page_hits = 0
        self.history = []  # History of operations
        
    def reset(self):
        """Reset the algorithm state"""
        self.ram = []
        self.swap_space = []
        self.page_faults = 0
        self.page_hits = 0
        self.history = []
        
    def access_page(self, page: int, reference_string: List[int], current_index: int) -> dict:
        """
        Access a page and return the result
        Returns: dict with operation details
        """
        raise NotImplementedError("Subclasses must implement access_page")


class FIFO(PageReplacementAlgorithm):
    """First-In-First-Out page replacement algorithm"""
    
    def __init__(self, ram_frames: int, swap_frames: int):
        super().__init__(ram_frames, swap_frames)
        self.queue = deque()  # Track insertion order
        
    def reset(self):
        super().reset()
        self.queue = deque()
        
    def access_page(self, page: int, reference_string: List[int], current_index: int) -> dict:
        """Access page using FIFO algorithm"""
        result = {
            'page': page,
            'is_hit': False,
            'is_fault': False,
            'swapped_out': None,
            'swapped_in': page,
            'ram_state': [],
            'swap_state': [],
            'message': ''
        }
        
        # Check if page is in RAM (Page Hit)
        if page in self.ram:
            self.page_hits += 1
            result['is_hit'] = True
            result['message'] = f"Page {page} found in RAM - PAGE HIT"
        else:
            # Page Fault occurred
            self.page_faults += 1
            result['is_fault'] = True
            
            # Check if page is in swap space
            if page in self.swap_space:
                result['message'] = f"Page {page} not in RAM, found in Swap Space - PAGE FAULT"
                self.swap_space.remove(page)
            else:
                result['message'] = f"Page {page} not in RAM or Swap - PAGE FAULT"
            
            # Check if RAM is full
            if len(self.ram) < self.ram_frames:
                # RAM has space, just add the page
                self.ram.append(page)
                self.queue.append(page)
                result['message'] += f"\nPage {page} loaded into RAM"
            else:
                # RAM is full, need to swap out oldest page
                victim_page = self.queue.popleft()
                self.ram.remove(victim_page)
                
                # Move victim to swap space if there's room
                if len(self.swap_space) < self.swap_frames:
                    self.swap_space.append(victim_page)
                    result['swapped_out'] = victim_page
                    result['message'] += f"\nPage {victim_page} swapped out to Swap Space"
                else:
                    # Swap space is full, discard oldest page in swap
                    discarded = self.swap_space.pop(0)
                    self.swap_space.append(victim_page)
                    result['swapped_out'] = victim_page
                    result['message'] += f"\nPage {discarded} discarded from Swap Space"
                    result['message'] += f"\nPage {victim_page} swapped out to Swap Space"
                
                # Load new page into RAM
                self.ram.append(page)
                self.queue.append(page)
                result['message'] += f"\nPage {page} loaded into RAM"
        
        result['ram_state'] = self.ram.copy()
        result['swap_state'] = self.swap_space.copy()
        self.history.append(result)
        
        return result


class LRU(PageReplacementAlgorithm):
    """Least Recently Used page replacement algorithm"""
    
    def __init__(self, ram_frames: int, swap_frames: int):
        super().__init__(ram_frames, swap_frames)
        self.usage_order = []  # Track usage order (most recent at end)
        
    def reset(self):
        super().reset()
        self.usage_order = []
        
    def access_page(self, page: int, reference_string: List[int], current_index: int) -> dict:
        """Access page using LRU algorithm"""
        result = {
            'page': page,
            'is_hit': False,
            'is_fault': False,
            'swapped_out': None,
            'swapped_in': page,
            'ram_state': [],
            'swap_state': [],
            'message': ''
        }
        
        # Check if page is in RAM (Page Hit)
        if page in self.ram:
            self.page_hits += 1
            result['is_hit'] = True
            result['message'] = f"Page {page} found in RAM - PAGE HIT"
            
            # Update usage order (move to most recent)
            self.usage_order.remove(page)
            self.usage_order.append(page)
        else:
            # Page Fault occurred
            self.page_faults += 1
            result['is_fault'] = True
            
            # Check if page is in swap space
            if page in self.swap_space:
                result['message'] = f"Page {page} not in RAM, found in Swap Space - PAGE FAULT"
                self.swap_space.remove(page)
            else:
                result['message'] = f"Page {page} not in RAM or Swap - PAGE FAULT"
            
            # Check if RAM is full
            if len(self.ram) < self.ram_frames:
                # RAM has space, just add the page
                self.ram.append(page)
                self.usage_order.append(page)
                result['message'] += f"\nPage {page} loaded into RAM"
            else:
                # RAM is full, need to swap out least recently used page
                victim_page = self.usage_order.pop(0)  # Least recently used
                self.ram.remove(victim_page)
                
                # Move victim to swap space if there's room
                if len(self.swap_space) < self.swap_frames:
                    self.swap_space.append(victim_page)
                    result['swapped_out'] = victim_page
                    result['message'] += f"\nPage {victim_page} (LRU) swapped out to Swap Space"
                else:
                    # Swap space is full, discard oldest page in swap
                    discarded = self.swap_space.pop(0)
                    self.swap_space.append(victim_page)
                    result['swapped_out'] = victim_page
                    result['message'] += f"\nPage {discarded} discarded from Swap Space"
                    result['message'] += f"\nPage {victim_page} (LRU) swapped out to Swap Space"
                
                # Load new page into RAM
                self.ram.append(page)
                self.usage_order.append(page)
                result['message'] += f"\nPage {page} loaded into RAM"
        
        result['ram_state'] = self.ram.copy()
        result['swap_state'] = self.swap_space.copy()
        self.history.append(result)
        
        return result


class Optimal(PageReplacementAlgorithm):
    """Optimal page replacement algorithm (Belady's algorithm)"""
    
    def reset(self):
        super().reset()
        
    def access_page(self, page: int, reference_string: List[int], current_index: int) -> dict:
        """Access page using Optimal algorithm"""
        result = {
            'page': page,
            'is_hit': False,
            'is_fault': False,
            'swapped_out': None,
            'swapped_in': page,
            'ram_state': [],
            'swap_state': [],
            'message': ''
        }
        
        # Check if page is in RAM (Page Hit)
        if page in self.ram:
            self.page_hits += 1
            result['is_hit'] = True
            result['message'] = f"Page {page} found in RAM - PAGE HIT"
        else:
            # Page Fault occurred
            self.page_faults += 1
            result['is_fault'] = True
            
            # Check if page is in swap space
            if page in self.swap_space:
                result['message'] = f"Page {page} not in RAM, found in Swap Space - PAGE FAULT"
                self.swap_space.remove(page)
            else:
                result['message'] = f"Page {page} not in RAM or Swap - PAGE FAULT"
            
            # Check if RAM is full
            if len(self.ram) < self.ram_frames:
                # RAM has space, just add the page
                self.ram.append(page)
                result['message'] += f"\nPage {page} loaded into RAM"
            else:
                # RAM is full, find optimal page to replace
                victim_page = self._find_optimal_victim(reference_string, current_index)
                self.ram.remove(victim_page)
                
                # Move victim to swap space if there's room
                if len(self.swap_space) < self.swap_frames:
                    self.swap_space.append(victim_page)
                    result['swapped_out'] = victim_page
                    result['message'] += f"\nPage {victim_page} (Optimal) swapped out to Swap Space"
                else:
                    # Swap space is full, discard oldest page in swap
                    discarded = self.swap_space.pop(0)
                    self.swap_space.append(victim_page)
                    result['swapped_out'] = victim_page
                    result['message'] += f"\nPage {discarded} discarded from Swap Space"
                    result['message'] += f"\nPage {victim_page} (Optimal) swapped out to Swap Space"
                
                # Load new page into RAM
                self.ram.append(page)
                result['message'] += f"\nPage {page} loaded into RAM"
        
        result['ram_state'] = self.ram.copy()
        result['swap_state'] = self.swap_space.copy()
        self.history.append(result)
        
        return result
    
    def _find_optimal_victim(self, reference_string: List[int], current_index: int) -> int:
        """
        Find the page that will not be used for the longest time in the future
        """
        future_refs = reference_string[current_index + 1:]
        
        # Dictionary to store next use distance for each page in RAM
        next_use = {}
        
        for page in self.ram:
            if page in future_refs:
                # Find the index of next use
                next_use[page] = future_refs.index(page)
            else:
                # Page will never be used again, return it immediately
                return page
        
        # Return the page with maximum next use distance
        if next_use:
            return max(next_use, key=next_use.get)
        else:
            # If no future references, return first page
            return self.ram[0]


class SwapSpaceSimulator:
    """Main Swap Space Simulator GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Swap Space Simulator - Operating Systems Project")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Color scheme
        self.colors = {
            'bg': '#f0f0f0',
            'frame_bg': '#ffffff',
            'hit_color': '#90EE90',  # Light green
            'fault_color': '#FFB6C1',  # Light red
            'swap_color': '#FFD700',  # Gold
            'ram_color': '#87CEEB',  # Sky blue
            'button_color': '#4CAF50',
            'reset_color': '#f44336',
            'next_color': '#2196F3'
        }
        
        # Simulator state
        self.algorithm = None
        self.reference_string = []
        self.current_step = 0
        self.is_started = False
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="🖥️ Swap Space Simulator",
            font=("Arial", 24, "bold"),
            bg=self.colors['bg'],
            fg='#333333'
        )
        title_label.pack(pady=(0, 10))
        
        # Input Frame
        input_frame = tk.LabelFrame(
            main_container,
            text="Configuration",
            font=("Arial", 12, "bold"),
            bg=self.colors['frame_bg'],
            padx=10,
            pady=10
        )
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: RAM, Swap, Page Size
        row1 = tk.Frame(input_frame, bg=self.colors['frame_bg'])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(row1, text="RAM Size (Frames):", font=("Arial", 10), bg=self.colors['frame_bg']).pack(side=tk.LEFT, padx=5)
        self.ram_size_var = tk.StringVar(value="3")
        tk.Entry(row1, textvariable=self.ram_size_var, width=10, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="Swap Space (Frames):", font=("Arial", 10), bg=self.colors['frame_bg']).pack(side=tk.LEFT, padx=5)
        self.swap_size_var = tk.StringVar(value="3")
        tk.Entry(row1, textvariable=self.swap_size_var, width=10, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="Page Size (KB):", font=("Arial", 10), bg=self.colors['frame_bg']).pack(side=tk.LEFT, padx=5)
        self.page_size_var = tk.StringVar(value="4")
        tk.Entry(row1, textvariable=self.page_size_var, width=10, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # Row 2: Algorithm Selection
        row2 = tk.Frame(input_frame, bg=self.colors['frame_bg'])
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(row2, text="Algorithm:", font=("Arial", 10), bg=self.colors['frame_bg']).pack(side=tk.LEFT, padx=5)
        self.algorithm_var = tk.StringVar(value="FIFO")
        algorithm_combo = ttk.Combobox(
            row2,
            textvariable=self.algorithm_var,
            values=["FIFO", "LRU", "Optimal"],
            state="readonly",
            width=15,
            font=("Arial", 10)
        )
        algorithm_combo.pack(side=tk.LEFT, padx=5)
        
        # Row 3: Page Reference String
        row3 = tk.Frame(input_frame, bg=self.colors['frame_bg'])
        row3.pack(fill=tk.X, pady=5)
        
        tk.Label(row3, text="Page Reference String:", font=("Arial", 10), bg=self.colors['frame_bg']).pack(side=tk.LEFT, padx=5)
        self.reference_var = tk.StringVar(value="1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5")
        tk.Entry(row3, textvariable=self.reference_var, width=50, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            row3,
            text="Generate Random",
            command=self._generate_random,
            bg='#FF9800',
            fg='white',
            font=("Arial", 9, "bold"),
            relief=tk.RAISED,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Control Buttons Frame
        control_frame = tk.Frame(main_container, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = tk.Button(
            control_frame,
            text="▶ START SIMULATION",
            command=self._start_simulation,
            bg=self.colors['button_color'],
            fg='white',
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = tk.Button(
            control_frame,
            text="➡ NEXT STEP",
            command=self._next_step,
            bg=self.colors['next_color'],
            fg='white',
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            state=tk.DISABLED,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            control_frame,
            text="🔄 RESET",
            command=self._reset_simulation,
            bg=self.colors['reset_color'],
            fg='white',
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Display Area
        display_area = tk.Frame(main_container, bg=self.colors['bg'])
        display_area.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel - RAM and Swap Space
        left_panel = tk.Frame(display_area, bg=self.colors['bg'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # RAM Frame
        ram_frame = tk.LabelFrame(
            left_panel,
            text="🎯 RAM (Physical Memory)",
            font=("Arial", 11, "bold"),
            bg=self.colors['frame_bg'],
            padx=10,
            pady=10
        )
        ram_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.ram_canvas = tk.Canvas(ram_frame, bg='white', height=150, relief=tk.SUNKEN, bd=2)
        self.ram_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Swap Space Frame
        swap_frame = tk.LabelFrame(
            left_panel,
            text="💾 Swap Space (Virtual Memory)",
            font=("Arial", 11, "bold"),
            bg=self.colors['frame_bg'],
            padx=10,
            pady=10
        )
        swap_frame.pack(fill=tk.BOTH, expand=True)
        
        self.swap_canvas = tk.Canvas(swap_frame, bg='white', height=150, relief=tk.SUNKEN, bd=2)
        self.swap_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right Panel - Status and Log
        right_panel = tk.Frame(display_area, bg=self.colors['bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Statistics Frame
        stats_frame = tk.LabelFrame(
            right_panel,
            text="📊 Statistics",
            font=("Arial", 11, "bold"),
            bg=self.colors['frame_bg'],
            padx=10,
            pady=10
        )
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Statistics display
        stats_container = tk.Frame(stats_frame, bg=self.colors['frame_bg'])
        stats_container.pack(fill=tk.X)
        
        # Current Page
        tk.Label(stats_container, text="Current Page:", font=("Arial", 10, "bold"), bg=self.colors['frame_bg']).grid(row=0, column=0, sticky='w', pady=2)
        self.current_page_label = tk.Label(stats_container, text="N/A", font=("Arial", 10), bg=self.colors['frame_bg'], fg='blue')
        self.current_page_label.grid(row=0, column=1, sticky='w', padx=10, pady=2)
        
        # Step
        tk.Label(stats_container, text="Step:", font=("Arial", 10, "bold"), bg=self.colors['frame_bg']).grid(row=1, column=0, sticky='w', pady=2)
        self.step_label = tk.Label(stats_container, text="0/0", font=("Arial", 10), bg=self.colors['frame_bg'])
        self.step_label.grid(row=1, column=1, sticky='w', padx=10, pady=2)
        
        # Page Hits
        tk.Label(stats_container, text="Page Hits:", font=("Arial", 10, "bold"), bg=self.colors['frame_bg']).grid(row=2, column=0, sticky='w', pady=2)
        self.hits_label = tk.Label(stats_container, text="0", font=("Arial", 10), bg=self.colors['frame_bg'], fg='green')
        self.hits_label.grid(row=2, column=1, sticky='w', padx=10, pady=2)
        
        # Page Faults
        tk.Label(stats_container, text="Page Faults:", font=("Arial", 10, "bold"), bg=self.colors['frame_bg']).grid(row=3, column=0, sticky='w', pady=2)
        self.faults_label = tk.Label(stats_container, text="0", font=("Arial", 10), bg=self.colors['frame_bg'], fg='red')
        self.faults_label.grid(row=3, column=1, sticky='w', padx=10, pady=2)
        
        # Hit Rate
        tk.Label(stats_container, text="Hit Rate:", font=("Arial", 10, "bold"), bg=self.colors['frame_bg']).grid(row=4, column=0, sticky='w', pady=2)
        self.hit_rate_label = tk.Label(stats_container, text="0.00%", font=("Arial", 10), bg=self.colors['frame_bg'])
        self.hit_rate_label.grid(row=4, column=1, sticky='w', padx=10, pady=2)
        
        # Operation Log Frame
        log_frame = tk.LabelFrame(
            right_panel,
            text="📝 Operation Log",
            font=("Arial", 11, "bold"),
            bg=self.colors['frame_bg'],
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=40,
            height=15,
            font=("Courier", 9),
            bg='#f9f9f9',
            relief=tk.SUNKEN,
            bd=2
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.log_text.tag_config('hit', foreground='green', font=("Courier", 9, "bold"))
        self.log_text.tag_config('fault', foreground='red', font=("Courier", 9, "bold"))
        self.log_text.tag_config('swap', foreground='orange', font=("Courier", 9, "bold"))
        self.log_text.tag_config('info', foreground='blue', font=("Courier", 9))
        self.log_text.tag_config('header', foreground='purple', font=("Courier", 9, "bold"))
        
    def _generate_random(self):
        """Generate random page reference string"""
        try:
            num_pages = random.randint(10, 20)
            max_page = random.randint(5, 10)
            pages = [random.randint(1, max_page) for _ in range(num_pages)]
            self.reference_var.set(", ".join(map(str, pages)))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate random sequence: {str(e)}")
    
    def _start_simulation(self):
        """Initialize and start the simulation"""
        try:
            # Validate inputs
            ram_frames = int(self.ram_size_var.get())
            swap_frames = int(self.swap_size_var.get())
            page_size = int(self.page_size_var.get())
            
            if ram_frames <= 0 or swap_frames <= 0 or page_size <= 0:
                messagebox.showerror("Invalid Input", "All sizes must be positive integers!")
                return
            
            # Parse reference string
            ref_string = self.reference_var.get().strip()
            if not ref_string:
                messagebox.showerror("Invalid Input", "Page reference string cannot be empty!")
                return
            
            self.reference_string = [int(x.strip()) for x in ref_string.split(',')]
            
            if not self.reference_string:
                messagebox.showerror("Invalid Input", "Invalid page reference string!")
                return
            
            # Initialize algorithm
            algorithm_name = self.algorithm_var.get()
            if algorithm_name == "FIFO":
                self.algorithm = FIFO(ram_frames, swap_frames)
            elif algorithm_name == "LRU":
                self.algorithm = LRU(ram_frames, swap_frames)
            elif algorithm_name == "Optimal":
                self.algorithm = Optimal(ram_frames, swap_frames)
            
            # Reset state
            self.current_step = 0
            self.is_started = True
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.NORMAL)
            
            # Clear displays
            self._update_displays(None)
            
            # Log initialization
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "="*50 + "\n", 'header')
            self.log_text.insert(tk.END, "SIMULATION STARTED\n", 'header')
            self.log_text.insert(tk.END, "="*50 + "\n", 'header')
            self.log_text.insert(tk.END, f"Algorithm: {algorithm_name}\n", 'info')
            self.log_text.insert(tk.END, f"RAM Frames: {ram_frames}\n", 'info')
            self.log_text.insert(tk.END, f"Swap Frames: {swap_frames}\n", 'info')
            self.log_text.insert(tk.END, f"Page Size: {page_size} KB\n", 'info')
            self.log_text.insert(tk.END, f"Reference String: {', '.join(map(str, self.reference_string))}\n", 'info')
            self.log_text.insert(tk.END, "="*50 + "\n\n", 'header')
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integer values!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start simulation: {str(e)}")
    
    def _next_step(self):
        """Execute next step in simulation"""
        if not self.is_started or self.current_step >= len(self.reference_string):
            messagebox.showinfo("Complete", "Simulation completed!")
            self.next_button.config(state=tk.DISABLED)
            return
        
        try:
            # Get current page
            current_page = self.reference_string[self.current_step]
            
            # Execute algorithm step
            result = self.algorithm.access_page(current_page, self.reference_string, self.current_step)
            
            # Update displays
            self._update_displays(result)
            
            # Log the operation
            self._log_operation(result)
            
            # Increment step
            self.current_step += 1
            
            # Check if simulation is complete
            if self.current_step >= len(self.reference_string):
                self.next_button.config(state=tk.DISABLED)
                self.log_text.insert(tk.END, "\n" + "="*50 + "\n", 'header')
                self.log_text.insert(tk.END, "SIMULATION COMPLETED\n", 'header')
                self.log_text.insert(tk.END, "="*50 + "\n", 'header')
                
                # Calculate final statistics
                total_accesses = self.algorithm.page_hits + self.algorithm.page_faults
                hit_rate = (self.algorithm.page_hits / total_accesses * 100) if total_accesses > 0 else 0
                
                self.log_text.insert(tk.END, f"\nFinal Statistics:\n", 'info')
                self.log_text.insert(tk.END, f"Total Page Accesses: {total_accesses}\n", 'info')
                self.log_text.insert(tk.END, f"Page Hits: {self.algorithm.page_hits}\n", 'hit')
                self.log_text.insert(tk.END, f"Page Faults: {self.algorithm.page_faults}\n", 'fault')
                self.log_text.insert(tk.END, f"Hit Rate: {hit_rate:.2f}%\n", 'info')
                
        except Exception as e:
            messagebox.showerror("Error", f"Error during simulation step: {str(e)}")
    
    def _update_displays(self, result):
        """Update RAM and Swap Space visual displays"""
        # Clear canvases
        self.ram_canvas.delete("all")
        self.swap_canvas.delete("all")
        
        if result is None:
            # Initial state
            self.current_page_label.config(text="N/A")
            self.step_label.config(text="0/0")
            self.hits_label.config(text="0")
            self.faults_label.config(text="0")
            self.hit_rate_label.config(text="0.00%")
            return
        
        # Update statistics
        self.current_page_label.config(text=str(result['page']))
        self.step_label.config(text=f"{self.current_step + 1}/{len(self.reference_string)}")
        self.hits_label.config(text=str(self.algorithm.page_hits))
        self.faults_label.config(text=str(self.algorithm.page_faults))
        
        total = self.algorithm.page_hits + self.algorithm.page_faults
        hit_rate = (self.algorithm.page_hits / total * 100) if total > 0 else 0
        self.hit_rate_label.config(text=f"{hit_rate:.2f}%")
        
        # Draw RAM frames
        ram_state = result['ram_state']
        ram_capacity = self.algorithm.ram_frames
        
        frame_width = 80
        frame_height = 80
        margin = 20
        
        for i in range(ram_capacity):
            x = margin + i * (frame_width + margin)
            y = margin
            
            # Determine color
            if i < len(ram_state):
                page = ram_state[i]
                if result['is_hit'] and page == result['page']:
                    color = self.colors['hit_color']
                elif result['is_fault'] and page == result['page']:
                    color = self.colors['fault_color']
                else:
                    color = self.colors['ram_color']
                
                # Draw filled rectangle
                self.ram_canvas.create_rectangle(
                    x, y, x + frame_width, y + frame_height,
                    fill=color, outline='black', width=2
                )
                
                # Draw page number
                self.ram_canvas.create_text(
                    x + frame_width/2, y + frame_height/2,
                    text=f"Page {page}",
                    font=("Arial", 12, "bold"),
                    fill='black'
                )
            else:
                # Empty frame
                self.ram_canvas.create_rectangle(
                    x, y, x + frame_width, y + frame_height,
                    fill='white', outline='gray', width=2, dash=(5, 5)
                )
                self.ram_canvas.create_text(
                    x + frame_width/2, y + frame_height/2,
                    text="Empty",
                    font=("Arial", 10),
                    fill='gray'
                )
        
        # Draw Swap Space frames
        swap_state = result['swap_state']
        swap_capacity = self.algorithm.swap_frames
        
        for i in range(swap_capacity):
            x = margin + i * (frame_width + margin)
            y = margin
            
            if i < len(swap_state):
                page = swap_state[i]
                
                # Highlight if just swapped
                if result['swapped_out'] == page:
                    color = self.colors['swap_color']
                else:
                    color = '#E0E0E0'
                
                # Draw filled rectangle
                self.swap_canvas.create_rectangle(
                    x, y, x + frame_width, y + frame_height,
                    fill=color, outline='black', width=2
                )
                
                # Draw page number
                self.swap_canvas.create_text(
                    x + frame_width/2, y + frame_height/2,
                    text=f"Page {page}",
                    font=("Arial", 12, "bold"),
                    fill='black'
                )
            else:
                # Empty frame
                self.swap_canvas.create_rectangle(
                    x, y, x + frame_width, y + frame_height,
                    fill='white', outline='gray', width=2, dash=(5, 5)
                )
                self.swap_canvas.create_text(
                    x + frame_width/2, y + frame_height/2,
                    text="Empty",
                    font=("Arial", 10),
                    fill='gray'
                )
    
    def _log_operation(self, result):
        """Log the operation details"""
        self.log_text.insert(tk.END, f"\n--- Step {self.current_step + 1} ---\n", 'header')
        self.log_text.insert(tk.END, f"Accessing Page: {result['page']}\n", 'info')
        
        # Determine type and log accordingly
        if result['is_hit']:
            self.log_text.insert(tk.END, "Result: PAGE HIT ✓\n", 'hit')
        else:
            self.log_text.insert(tk.END, "Result: PAGE FAULT ✗\n", 'fault')
        
        # Log message
        for line in result['message'].split('\n'):
            if line:
                if 'HIT' in line:
                    self.log_text.insert(tk.END, line + "\n", 'hit')
                elif 'FAULT' in line:
                    self.log_text.insert(tk.END, line + "\n", 'fault')
                elif 'swapped' in line.lower():
                    self.log_text.insert(tk.END, line + "\n", 'swap')
                else:
                    self.log_text.insert(tk.END, line + "\n", 'info')
        
        # Show current state
        self.log_text.insert(tk.END, f"RAM: {result['ram_state']}\n", 'info')
        self.log_text.insert(tk.END, f"Swap: {result['swap_state']}\n", 'info')
        
        # Auto-scroll to bottom
        self.log_text.see(tk.END)
    
    def _reset_simulation(self):
        """Reset the simulation"""
        self.is_started = False
        self.current_step = 0
        self.algorithm = None
        self.reference_string = []
        
        # Reset UI
        self.start_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)
        
        # Clear displays
        self.ram_canvas.delete("all")
        self.swap_canvas.delete("all")
        self.log_text.delete(1.0, tk.END)
        
        # Reset statistics
        self.current_page_label.config(text="N/A")
        self.step_label.config(text="0/0")
        self.hits_label.config(text="0")
        self.faults_label.config(text="0")
        self.hit_rate_label.config(text="0.00%")
        
        self.log_text.insert(tk.END, "Simulation reset. Ready to start.\n", 'info')


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SwapSpaceSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
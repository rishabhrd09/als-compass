"""
ALS Research Manager - Desktop GUI Application
Local tool for managing research updates without needing a web server
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

class ResearchManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ALS Research Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#f5f5f5')
        
        # File paths
        self.research_file = 'data/research_updates.json'
        
        # Configure OpenAI
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.create_widgets()
        self.load_research_list()
    
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="🔬 ALS Research Updates Manager", 
                        font=('Helvetica', 18, 'bold'), bg='#f5f5f5', fg='#2c3e50')
        title.pack(pady=20)
        
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Tab 1: Current Research
        self.tab_current = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_current, text='📋 Current Research')
        self.create_current_tab()
        
        # Tab 2: Add New
        self.tab_add = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_add, text='➕ Add New')
        self.create_add_tab()
        
        # Tab 3: AI Fetch
        self.tab_ai = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ai, text='🤖 AI Auto-Fetch')
        self.create_ai_tab()
    
    def create_current_tab(self):
        # Scrolled list
        frame = ttk.Frame(self.tab_current)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        self.research_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set,
                                           font=('Helvetica', 11), height=20)
        self.research_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.research_listbox.yview)
        
        # Buttons
        btn_frame = ttk.Frame(self.tab_current)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="🗑️ Delete Selected", 
                  command=self.delete_research).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh List", 
                  command=self.load_research_list).pack(side='left', padx=5)
    
    def create_add_tab(self):
        # Form frame
        form_frame = ttk.Frame(self.tab_add)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Treatment Name
        ttk.Label(form_frame, text="Treatment Name *", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(form_frame, width=50)
        self.name_entry.grid(row=1, column=0, pady=5)
        
        # Company
        ttk.Label(form_frame, text="Company/Organization *", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=5)
        self.company_entry = ttk.Entry(form_frame, width=50)
        self.company_entry.grid(row=3, column=0, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description * (use • for bullet points)", 
                 font=('Helvetica', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        self.description_text = scrolledtext.ScrolledText(form_frame, width=50, height=5)
        self.description_text.grid(row=5, column=0, pady=5)
        
        # Link
        ttk.Label(form_frame, text="Official Website URL *", font=('Helvetica', 10, 'bold')).grid(
            row=6, column=0, sticky='w', pady=5)
        self.link_entry = ttk.Entry(form_frame, width=50)
        self.link_entry.grid(row=7, column=0, pady=5)
        
        # Link Name
        ttk.Label(form_frame, text="Link Display Name *", font=('Helvetica', 10, 'bold')).grid(
            row=8, column=0, sticky='w', pady=5)
        self.link_name_entry = ttk.Entry(form_frame, width=50)
        self.link_name_entry.grid(row=9, column=0, pady=5)
        
        # Add Button
        ttk.Button(form_frame, text="✅ Add Research Update", 
                  command=self.add_research).grid(row=10, column=0, pady=20)
    
    def create_ai_tab(self):
        frame = ttk.Frame(self.tab_ai)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Info
        info_text = """
🤖 AI-Powered Research Auto-Fetch (Using OpenAI GPT-4)

The AI will search for the latest ALS clinical trials and research updates.
You'll be able to review the results before adding them.
        """
        info_label = tk.Label(frame, text=info_text, font=('Helvetica', 10),
                             bg='#e3f2fd', fg='#0c5460', justify='left', padx=10, pady=10)
        info_label.pack(fill='x', pady=10)
        
        # Fetch Button
        ttk.Button(frame, text="🔍 Fetch Latest Research with AI", 
                  command=self.fetch_with_ai).pack(pady=20)
        
        # Results area
        ttk.Label(frame, text="AI Results:", font=('Helvetica', 10, 'bold')).pack(anchor='w')
        self.ai_results_text = scrolledtext.ScrolledText(frame, width=70, height=20)
        self.ai_results_text.pack(fill='both', expand=True, pady=10)
    
    def load_json(self):
        """Load JSON file"""
        if not os.path.exists(self.research_file):
            os.makedirs(os.path.dirname(self.research_file), exist_ok=True)
            with open(self.research_file, 'w') as f:
                json.dump([], f)
            return []
        
        with open(self.research_file, 'r') as f:
            return json.load(f)
    
    def save_json(self, data):
        """Save to JSON file"""
        with open(self.research_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def get_next_id(self, data):
        """Get next ID"""
        if not data:
            return 1
        return max(item['id'] for item in data) + 1
    
    def load_research_list(self):
        """Load research into listbox"""
        self.research_listbox.delete(0, tk.END)
        data = self.load_json()
        active = [r for r in data if r.get('status') == 'active']
        
        for item in active:
            display = f"{item['name']} | {item['company']}"
            self.research_listbox.insert(tk.END, display)
            self.research_listbox.itemconfig(tk.END, {'bg': '#f0f0f0'})
    
    def add_research(self):
        """Add new research"""
        name = self.name_entry.get().strip()
        company = self.company_entry.get().strip()
        description = self.description_text.get('1.0', 'end-1c').strip()
        link = self.link_entry.get().strip()
        link_name = self.link_name_entry.get().strip()
        
        if not all([name, company, description, link, link_name]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        data = self.load_json()
        new_research = {
            'id': self.get_next_id(data),
            'name': name,
            'company': company,
            'description': description,
            'link': link,
            'link_name': link_name,
            'date_added': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active'
        }
        
        data.append(new_research)
        self.save_json(data)
        
        messagebox.showinfo("Success", "Research update added successfully!")
        
        # Clear form
        self.name_entry.delete(0, tk.END)
        self.company_entry.delete(0, tk.END)
        self.description_text.delete('1.0', tk.END)
        self.link_entry.delete(0, tk.END)
        self.link_name_entry.delete(0, tk.END)
        
        # Refresh list
        self.load_research_list()
        self.notebook.select(0)  # Switch to current tab
    
    def delete_research(self):
        """Delete selected research"""
        selection = self.research_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a research item to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this research?"):
            return
        
        idx = selection[0]
        data = self.load_json()
        active = [r for r in data if r.get('status') == 'active']
        
        if idx < len(active):
            item_to_delete = active[idx]
            data = [r for r in data if r['id'] != item_to_delete['id']]
            self.save_json(data)
            self.load_research_list()
            messagebox.showinfo("Success", "Research deleted!")
    
    def fetch_with_ai(self):
        """Fetch research using AI"""
        self.ai_results_text.delete('1.0', tk.END)
        self.ai_results_text.insert('1.0', "🔄 Searching for latest research using OpenAI...\n\n")
        self.root.update()
        
        try:
            prompt = """
            Find the 3 most recent and credible ALS (Amyotrophic Lateral Sclerosis) clinical trials or research updates from December 2024.
            
            For each research update, provide:
            1. Treatment/Drug Name
            2. Company/Organization Name
            3. Brief Description (include FDA approval status, phase, mechanism of action) - use bullet points with • separator
            4. Official Website URL
            5. Display name for the link (usually company name or organization)
            
            Format your response as a JSON array with these exact keys:
            [
                {
                    "name": "Treatment Name",
                    "company": "Company Name",
                    "description": "Status • Phase • Description",
                    "link": "https://official-url.com",
                    "link_name": "Link Display Name"
                }
            ]
            
            Return ONLY valid JSON, no additional text or explanations.
            """
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that finds the latest ALS research updates and returns them ONLY as valid JSON, with no additional text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Debug: Show what we received
            if not response_text:
                raise ValueError("Empty response from OpenAI")
            
            # Try to parse JSON with multiple fallback methods
            ai_results = None
            
            # Method 1: Direct parse
            try:
                ai_results = json.loads(response_text)
                # If it's a dict with 'research' or similar key
                if isinstance(ai_results, dict):
                    if 'research' in ai_results:
                        ai_results = ai_results['research']
                    elif 'treatments' in ai_results:
                        ai_results = ai_results['treatments']
                    elif 'results' in ai_results:
                        ai_results = ai_results['results']
            except json.JSONDecodeError:
                pass
            
            # Method 2: Remove markdown code blocks
            if ai_results is None:
                cleaned_text = response_text
                if '```json' in cleaned_text:
                    cleaned_text = cleaned_text.split('```json')[1].split('```')[0]
                elif '```' in cleaned_text:
                    cleaned_text = cleaned_text.split('```')[1].split('```')[0]
                
                ai_results = json.loads(cleaned_text.strip())
            
            # Ensure it's a list
            if not isinstance(ai_results, list):
                raise ValueError("Response is not a list of research items")
            
            # Display results
            self.ai_results_text.delete('1.0', tk.END)
            self.ai_results_text.insert('1.0', f"✅ Found {len(ai_results)} research updates!\n\n")
            
            for i, result in enumerate(ai_results, 1):
                self.ai_results_text.insert(tk.END, f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                self.ai_results_text.insert(tk.END, f"#{i} {result.get('name', 'Unknown')}\n", 'bold')
                self.ai_results_text.insert(tk.END, f"Company: {result.get('company', 'Unknown')}\n")
                self.ai_results_text.insert(tk.END, f"Description: {result.get('description', 'No description')}\n")
                self.ai_results_text.insert(tk.END, f"Link: {result.get('link', 'No link')}\n\n")
            
            # Ask to add
            if messagebox.askyesno("Add Research?", 
                                  f"Found {len(ai_results)} research updates.\n\nAdd all to your research list?"):
                data = self.load_json()
                next_id = self.get_next_id(data)
                
                for i, result in enumerate(ai_results):
                    result['id'] = next_id + i
                    result['date_added'] = datetime.now().strftime('%Y-%m-%d')
                    result['status'] = 'active'
                    data.append(result)
                
                self.save_json(data)
                self.load_research_list()
                messagebox.showinfo("Success", f"Added {len(ai_results)} research updates!")
        
        except json.JSONDecodeError as e:
            self.ai_results_text.delete('1.0', tk.END)
            self.ai_results_text.insert('1.0', f"❌ JSON Parse Error: {str(e)}\n\n")
            self.ai_results_text.insert(tk.END, "Raw response:\n")
            self.ai_results_text.insert(tk.END, response_text[:500] if 'response_text' in locals() else "No response")
        except Exception as e:
            self.ai_results_text.delete('1.0', tk.END)
            self.ai_results_text.insert('1.0', f"❌ Error: {str(e)}\n\n")
            self.ai_results_text.insert(tk.END, "Please check your OPENAI_API_KEY in .env file\n\n")
            self.ai_results_text.insert(tk.END, f"Error type: {type(e).__name__}")

def main():
    root = tk.Tk()
    app = ResearchManagerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔬 ALS Research Manager - Desktop Application")
    print("="*60)
    print("\nLaunching GUI...")
    print("="*60 + "\n")
    main()

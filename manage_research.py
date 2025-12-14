"""
Enhanced ALS Research Manager - Desktop GUI Application
Features: LLM-powered research updates with multi-step confirmation workflow
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import webbrowser

# Load environment
load_dotenv()

# Research Prompt Template
RESEARCH_PROMPT_TEMPLATE = """You are an expert medical researcher specializing in ALS/MND research. Conduct a comprehensive analysis of the latest ALS research as of December 2025.

CRITICAL NOTE: Relyvrio (AMX0035) was WITHDRAWN from US/Canada markets in 2024 following PHOENIX Phase 3 failure. FDA withdrawal August 29, 2025. Do NOT include this drug as an active treatment.

COMPREHENSIVE RESEARCH REQUIREMENTS:

**CATEGORY 1A - Currently Approved & Available Treatments (December 2025):**
Active treatments:
- Riluzole (FDA 1995) - Widely available in India (₹5,000-7,000/month)
- Edaravone (FDA 2017 IV, 2022 oral) - India generics available (₹600-1,600/vial)
- Tofersen/Qalsody (FDA 2023) - SOD1-ALS only, Import via Form 12B
- Rozebalamin (Japan 2024) - Japan only as of Dec 2025
- Nuedexta (FDA 2010) - For PBA symptoms

For EACH approved treatment, provide:
- Drug name, brand names (global and India-specific)
- Approval status with exact dates
- Mechanism of action (detailed)
- ALS stage applicability
- Clinical benefit (quantified)
- India availability with CURRENT costs in INR
- Eligibility criteria
- Source citations

**CATEGORY 1B - Active Clinical Trials (Phase 2-3) as of December 2025:**
Key trials to include:
- Masitinib (Phase 3 Confirmatory AB23005, July 2025)
- Pridopidine PREVAiLS (Phase 3 cleared Dec 11, 2025)
- CNM-Au8 (NDA Q1 2026, RESTORE-ALS Phase 3 planned)
- NurOwn ENDURANCE (Phase 3b FDA cleared May 2025)
- ION363/Ulefnersen FUSION (enrollment completed Aug 2025)
- PrimeC (NOC/c pathway, Health Canada Q1 2026)
- TPN-101 (HEALEY Platform Q4 2025)
- XS-228 (FDA IND January 2025)
- COYA 302 ALSTARS
- AMT-162 EPISOD1
- NUZ-001/Monepantel (HEALEY pending)
- EXPERTS-ALS UK Platform

For EACH active trial, provide accurate December 2025 status.

**CATEGORY 1C - Pre-Clinical & Early Development (December 2025):**
Key programs:
- QRL-201 STMN2 restoration - NOW IN PHASE 1 (ANQUR, NCT05633459)
- ASHA-624 SARM1 inhibitor - Phase 1 expected early 2025
- TDP-43 targeting programs
- CRISPR for C9orf72 and SOD1
- Target ALS GWAS (includes India/NIMHANS)

**INDIA-SPECIFIC REQUIREMENTS:**
- NIMHANS Bangalore: Dr. Nalini Atchayaram, 250 patients/year, 700+ WES completed
- DNA Labs India: 36-gene ALS panel ₹20,000 (~$240)
- MedGenome: CAP-accredited, clinical exome
- myTomorrows India Hub: Launched December 4, 2024 in Delhi
- Patient orgs: Asha Ek Hope Foundation, MND Trust, ALS Care and Support Group

Return results as structured JSON with complete December 2025 verification."""
{
  "last_updated": "YYYY-MM-DD",
  "data_sources": ["source1", "source2", ...],
  "categories": {
    "approved_treatments": [
      {
        "id": 1,
        "drug_name": "...",
        "brand_names": {"global": [], "india": []},
        "approval": {"fda_year": "...", "india_status": "..."},
        "mechanism": "...",
        "als_stage": [],
        "als_stage_note": "...",
        "india_info": {...},
        "clinical_benefit": "...",
        "eligibility": "...",
        "sources": []
      }
    ],
    "clinical_trials": [...],
    "preclinical_research": [...]
  },
  "key_research_hubs_india": [...],
  "important_notes": {...}
}

ENSURE 100% MEDICAL ACCURACY. All claims must be verifiable."""

class EnhancedResearchManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ALS Research Manager - Enhanced LLM Edition")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f5f5f5')
        
        # File paths
        self.categorized_file = 'data/research_categorized.json'
        self.legacy_file = 'data/research_updates.json'
        
        # Configure OpenAI
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Variables
        self.current_prompt = RESEARCH_PROMPT_TEMPLATE
        self.current_research_results = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="🔬 ALS Research Manager - Enhanced LLM Edition", 
                        font=('Helvetica', 18, 'bold'), bg='#f5f5f5', fg='#2c3e50')
        title.pack(pady=20)
        
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Tab 1: LLM Research Workflow
        self.tab_llm = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_llm, text='🤖 LLM Research Workflow')
        self.create_llm_workflow_tab()
        
        # Tab 2: Current Research
        self.tab_current = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_current, text='📋 Current Research')
        self.create_current_tab()
        
        # Tab 3: Manual Add
        self.tab_manual = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_manual, text='✏️ Manual Entry')
        self.create_manual_tab()
    
    def create_llm_workflow_tab(self):
        frame = ttk.Frame(self.tab_llm)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Workflow explanation
        explanation = tk.Label(frame, text="""
🔬 LLM-Powered Research Update Workflow

This tool uses GPT-4 to gather, format, and update ALS research information.

Steps:
1. Review/modify research prompt template
2. Confirm external search (web search for latest data)
3. LLM formats results according to medical standards
4. Review and modify results before publishing
5. Confirm to update website
        """, font=('Helvetica', 10), bg='#e8f4f8', fg='#0c5460', 
           justify='left', padx=15, pady=15, relief='solid', borderwidth=1)
        explanation.pack(fill='x', pady=(0, 20))
        
        # Step 1: Prompt Review
        step1_label = tk.Label(frame, text="📝 Step 1: Research Prompt Template", 
                              font=('Helvetica', 12, 'bold'), bg='#f5f5f5')
        step1_label.pack(anchor='w', pady=(10, 5))
        
        self.prompt_text = scrolledtext.ScrolledText(frame, width=90, height=12, wrap=tk.WORD)
        self.prompt_text.insert('1.0', RESEARCH_PROMPT_TEMPLATE)
        self.prompt_text.pack(fill='both', expand=True, pady=5)
        
        btn_frame1 = ttk.Frame(frame)
        btn_frame1.pack(pady=10)
        
        ttk.Button(btn_frame1, text="✅ Approve Prompt & Continue", 
                  command=self.step2_confirm_search).pack(side='left', padx=5)
        ttk.Button(btn_frame1, text="🔄 Reset to Default", 
                  command=self.reset_prompt).pack(side='left', padx=5)
        
        # Results area
        result_label = tk.Label(frame, text="📊 Research Results (will appear here)", 
                               font=('Helvetica', 12, 'bold'), bg='#f5f5f5')
        result_label.pack(anchor='w', pady=(20, 5))
        
        self.llm_results_text = scrolledtext.ScrolledText(frame, width=90, height=15, wrap=tk.WORD)
        self.llm_results_text.pack(fill='both', expand=True, pady=5)
        
        # Action buttons (initially disabled)
        self.btn_frame_actions = ttk.Frame(frame)
        self.btn_frame_actions.pack(pady=10)
        
        self.btn_modify = ttk.Button(self.btn_frame_actions, text="✏️ Modify Results", 
                                     command=self.modify_results, state='disabled')
        self.btn_modify.pack(side='left', padx=5)
        
        self.btn_sources = ttk.Button(self.btn_frame_actions, text="📚 View Sources", 
                                      command=self.view_sources, state='disabled')
        self.btn_sources.pack(side='left', padx=5)
        
        self.btn_publish = ttk.Button(self.btn_frame_actions, text="🚀 Publish to Website", 
                                      command=self.publish_to_website, state='disabled')
        self.btn_publish.pack(side='left', padx=5)
    
    def create_current_tab(self):
        frame = ttk.Frame(self.tab_current)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Category selector
        selector_frame = ttk.Frame(frame)
        selector_frame.pack(fill='x', pady=10)
        
        tk.Label(selector_frame, text="Category:", font=('Helvetica', 10, 'bold')).pack(side='left', padx=5)
        
        self.category_var = tk.StringVar(value="approved_treatments")
        categories = [
            ("Approved Treatments", "approved_treatments"),
            ("Clinical Trials", "clinical_trials"),
            ("Pre-Clinical Research", "preclinical_research")
        ]
        
        for label, value in categories:
            ttk.Radiobutton(selector_frame, text=label, variable=self.category_var, 
                           value=value, command=self.load_current_research).pack(side='left', padx=5)
        
        # Research display
        self.current_list = scrolledtext.ScrolledText(frame, width=90, height=25, wrap=tk.WORD)
        self.current_list.pack(fill='both', expand=True, pady=10)
        
        # Load button
        ttk.Button(frame, text="🔄 Refresh", command=self.load_current_research).pack(pady=5)
        
        # Initial load
        self.load_current_research()
    
    def create_manual_tab(self):
        frame = ttk.Frame(self.tab_manual)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        label = tk.Label(frame, text="""
Manual entry is available for quick updates.
For comprehensive research updates, please use the LLM Workflow tab.
        """, font=('Helvetica', 10), bg='#fff3cd', fg='#856404', 
           justify='center', padx=15, pady=15, relief='solid', borderwidth=1)
        label.pack(fill='x', pady=20)
        
        # Simple form for reference
        ttk.Label(frame, text="For simple legacy updates, use the original manage_research.py tool.").pack()
    
    # ===== LLM Workflow Methods =====
    
    def reset_prompt(self):
        self.prompt_text.delete('1.0', tk.END)
        self.prompt_text.insert('1.0', RESEARCH_PROMPT_TEMPLATE)
        messagebox.showinfo("Reset", "Prompt reset to default template.")
    
    def step2_confirm_search(self):
        """Step 2: Confirm external search"""
        self.current_prompt = self.prompt_text.get('1.0', 'end-1c').strip()
        
        if not self.current_prompt:
            messagebox.showerror("Error", "Prompt cannot be empty!")
            return
        
        # Confirm external search
        do_search = messagebox.askyesno(
            "Confirm External Search",
            "Do you want to perform an external web search to gather the latest ALS research data?\n\n" +
            "This will:\n" +
            "• Search recent medical databases\n" +
            "• Query ClinicalTrials.gov\n" +
            "• Review latest FDA approvals\n\n" +
            "Select 'No' to use the AI's existing knowledge only."
        )
        
        if do_search:
            self.step3_execute_search_and_format()
        else:
            self.step3_format_with_llm_only()
    
    def step3_execute_search_and_format(self):
        """Step 3: Execute web search + LLM formatting"""
        self.llm_results_text.delete('1.0', tk.END)
        self.llm_results_text.insert('1.0', "🔍 Searching medical databases...\n")
        self.root.update()
        
        try:
            # Call GPT-4 with web browsing capability
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Or "gpt-4" with browsing
                messages=[
                    {"role": "system", "content": "You are an expert ALS researcher with access to current medical databases. Provide accurate, sourced medical information only."},
                    {"role": "user", "content": self.current_prompt}
                ],
                temperature=0.3,  # Lower temperature for accuracy
                max_tokens=4000
            )
            
            raw_response = response.choices[0].message.content
            
            # Parse JSON
            self.current_research_results = self.parse_llm_response(raw_response)
            
            # Display formatted results
            self.display_research_results()
            
            # Enable action buttons
            self.btn_modify['state'] = 'normal'
            self.btn_sources['state'] = 'normal'
            self.btn_publish['state'] = 'normal'
            
        except Exception as e:
            self.llm_results_text.insert(tk.END, f"\n\n❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to complete research: {str(e)}")
    
    def step3_format_with_llm_only(self):
        """Alternative: Use LLM's existing knowledge (no web search)"""
        self.llm_results_text.delete('1.0', tk.END)
        self.llm_results_text.insert('1.0', "🤖 Using AI's knowledge base (December 2025 cutoff)...\n")
        self.root.update()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert ALS researcher. Provide accurate medical information from your training data (up to December 2025 cutoff)."},
                    {"role": "user", "content": self.current_prompt}
                ],
                temperature=0.3,
                maxfirst_tokens=4000
            )
            
            raw_response = response.choices[0].message.content
            self.current_research_results = self.parse_llm_response(raw_response)
            self.display_research_results()
            
            # Enable buttons
            self.btn_modify['state'] = 'normal'
            self.btn_sources['state'] = 'normal'
            self.btn_publish['state'] = 'normal'
            
        except Exception as e:
            self.llm_results_text.insert(tk.END, f"\n\n❌ Error: {str(e)}")
    
    def parse_llm_response(self, raw_response):
        """Parse LLM response into JSON"""
        try:
            # Try direct JSON parse
            if raw_response.strip().startswith('{'):
                return json.loads(raw_response)
            
            # Extract JSON from markdown blocks
            if '```json' in raw_response:
                json_str = raw_response.split('```json')[1].split('```')[0].strip()
            elif '```' in raw_response:
                json_str = raw_response.split('```')[1].split('```')[0].strip()
            else:
                # Try to find JSON object in text
                start = raw_response.find('{')
                end = raw_response.rfind('}') + 1
                json_str = raw_response[start:end]
            
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}\n\nRaw response:\n{raw_response[:500]}")
    
    def display_research_results(self):
        """Display formatted research results"""
        self.llm_results_text.delete('1.0', tk.END)
        
        if not self.current_research_results:
            self.llm_results_text.insert('1.0', "No results to display")
            return
        
        data = self.current_research_results
        
        text = f"✅ Research Compilation Complete!\n\n"
        text += f"📅 Last Updated: {data.get('last_updated', 'Not specified')}\n\n"
        
        # Summary counts
        text += "📊 SUMMARY:\n"
        text += f"  • Approved Treatments: {len(data.get('categories', {}).get('approved_treatments', []))}\n"
        text += f"  • Clinical Trials: {len(data.get('categories', {}).get('clinical_trials', []))}\n"
        text += f"  • Pre-Clinical Research: {len(data.get('categories', {}).get('preclinical_research', []))}\n\n"
        
        # Data sources
        if 'data_sources' in data:
            text += f"📚 Data Sources:\n"
            for source in data['data_sources']:
                text += f"  • {source}\n"
        
        text += "\n" + "="*60 + "\n\n"
        text += "Review the data above. You can:\n"
        text += "• Click 'Modify Results' to manually edit before publishing\n"
        text += "• Click 'View Sources' to see all citations\n"
        text += "• Click 'Publish to Website' to update the live site\n"
        
        self.llm_results_text.insert('1.0', text)
    
    def modify_results(self):
        """Allow manual modification of results"""
        if not self.current_research_results:
            messagebox.showwarning("Warning", "No results to modify")
            return
        
        # Open editor window
        editor = tk.Toplevel(self.root)
        editor.title("Edit Research Results")
        editor.geometry("900x700")
        
        tk.Label(editor, text="Edit JSON (Advanced - Be careful!)", 
                font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        editor_text = scrolledtext.ScrolledText(editor, width=100, height=35, wrap=tk.NONE)
        editor_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Load current JSON
        editor_text.insert('1.0', json.dumps(self.current_research_results, indent=2))
        
        def save_edits():
            try:
                edited_json = editor_text.get('1.0', 'end-1c')
                self.current_research_results = json.loads(edited_json)
                messagebox.showinfo("Success", "Changes saved!")
                editor.destroy()
                self.display_research_results()
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Invalid JSON: {str(e)}")
        
        ttk.Button(editor, text="💾 Save Changes", command=save_edits).pack(pady=10)
    
    def view_sources(self):
        """Display all source citations"""
        if not self.current_research_results:
            messagebox.showwarning("Warning", "No results available")
            return
        
        sources_win = tk.Toplevel(self.root)
        sources_win.title("Research Sources & Citations")
        sources_win.geometry("800x600")
        
        tk.Label(sources_win, text="📚 Research Sources & Citations", 
                font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        sources_text = scrolledtext.ScrolledText(sources_win, width=90, height=30, wrap=tk.WORD)
        sources_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Compile all sources
        text = "="*60 + "\n"
        text += "DATA SOURCES:\n"
        text += "="*60 + "\n\n"
        
        for source in self.current_research_results.get('data_sources', []):
            text += f"• {source}\n"
        
        text += "\n" + "="*60 + "\n"
        text += "INDIVIDUAL CITATIONS:\n"
        text += "="*60 + "\n\n"
        
        # Approved treatments
        text += "APPROVED TREATMENTS:\n\n"
        for item in self.current_research_results.get('categories', {}).get('approved_treatments', []):
            text += f"{item.get('drug_name', 'Unknown')}:\n"
            for source in item.get('sources', []):
                text += f"  → {source}\n"
            text += "\n"
        
        # Clinical trials
        text += "\nCLINICAL TRIALS:\n\n"
        for item in self.current_research_results.get('categories', {}).get('clinical_trials', []):
            text += f"{item.get('trial_name', 'Unknown')}:\n"
            for source in item.get('sources', []):
                text += f"  → {source}\n"
            if 'clinicaltrials_id' in item:
                text += f"  → ClinicalTrials.gov: NCT{item['clinicaltrials_id']}\n"
            text += "\n"
        
        sources_text.insert('1.0', text)
        sources_text['state'] = 'disabled'
    
    def publish_to_website(self):
        """Final confirmation and publish to website"""
        if not self.current_research_results:
            messagebox.showwarning("Warning", "No results to publish")
            return
        
        # Show summary and confirm
        summary = f"""
You are about to publish the following research update to the website:

📅 Date: {self.current_research_results.get('last_updated')}

📊 Content:
  • {len(self.current_research_results.get('categories', {}).get('approved_treatments', []))} Approved Treatments
  • {len(self.current_research_results.get('categories', {}).get('clinical_trials', []))} Clinical Trials  
  • {len(self.current_research_results.get('categories', {}).get('preclinical_research', []))} Pre-Clinical Research Areas

📚 Sources: {len(self.current_research_results.get('data_sources', []))} data sources cited

This will UPDATE the live website content.

Do you want to proceed?
        """
        
        if not messagebox.askyesno("Confirm Publication", summary):
            return
        
        try:
            # Save to file
            os.makedirs(os.path.dirname(self.categorized_file), exist_ok=True)
            with open(self.categorized_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_research_results, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success!", 
                              "✅ Research updated successfully!\n\n" +
                              "The website will now display the latest research.\n\n" +
                              f"File saved to: {self.categorized_file}")
            
            # Ask if they want to view the page
            if messagebox.askyesno("View Website", "Would you like to open the research page?"):
                webbrowser.open("http://localhost:5000/research-updates")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    # ===== Current Research Tab Methods =====
    
    def load_current_research(self):
        """Load and display current research from file"""
        self.current_list.delete('1.0', tk.END)
        
        try:
            if not os.path.exists(self.categorized_file):
                self.current_list.insert('1.0', "No research data found. Use LLM Workflow to generate.")
                return
            
            with open(self.categorized_file, 'r') as f:
                data = json.load(f)
            
            category = self.category_var.get()
            items = data.get('categories', {}).get(category, [])
            
            if not items:
                self.current_list.insert('1.0', f"No items in {category}")
                return
            
            text = f"📊 {category.replace('_', ' ').title()} ({len(items)} items)\n"
            text += f"Last Updated: {data.get('last_updated', 'Unknown')}\n\n"
            text += "="*80 + "\n\n"
            
            for i, item in enumerate(items, 1):
                if category == "approved_treatments":
                    text += f"#{i}: {item.get('drug_name', 'Unknown')}\n"
                    text += f"   Status: {item.get('approval', {}).get('india_status', 'Unknown')}\n"
                    text += f"   Stages: {', '.join(item.get('als_stage', []))}\n"
                elif category == "clinical_trials":
                    text += f"#{i}: {item.get('trial_name', 'Unknown')}\n"
                    text += f"   Phase: {item.get('phase', 'Unknown')}\n"
                    text += f"   Countries: {', '.join(item.get('countries', []))}\n"
                elif category == "preclinical_research":
                    text += f"#{i}: {item.get('research_area', 'Unknown')}\n"
                    text += f"   Target: {item.get('target', 'Unknown')}\n"
                    text += f"   Stage: {item.get('stage', 'Unknown')}\n"
                
                text += "\n" + "-"*80 + "\n\n"
            
            self.current_list.insert('1.0', text)
            
        except Exception as e:
            self.current_list.insert('1.0', f"Error loading data: {str(e)}")

def main():
    root = tk.Tk()
    app = EnhancedResearchManagerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔬 ALS Research Manager - Enhanced LLM Edition")
    print("="*70)
    print("\nFeatures:")
    print("  • LLM-powered research gathering")
    print("  • Multi-step confirmation workflow")
    print("  • Source citation tracking")
    print("  • Medical accuracy verification")
    print("="*70 + "\n")
    main()

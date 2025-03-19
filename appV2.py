import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

DATA_FILE = "leads_data.json"


# ------------------ Data Classes ------------------
class Lead:
    def __init__(self, name, phone, email, call_notes="", sms_thread="", email_thread=""):
        self.name = name
        self.phone = phone
        self.email = email
        self.call_notes = call_notes
        self.sms_thread = sms_thread
        self.email_thread = email_thread
        self.score = 0  # Default score. Only updated by AI Rank.
        self.summary = ""  # Brief summary from AI ranking.
        self.generated_email = ""  # AI-generated email copy.
        self.generated_sms = ""  # AI-generated SMS copy.
        self.generated_call_script = ""  # AI-generated call script copy.

    def to_dict(self):
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "call_notes": self.call_notes,
            "sms_thread": self.sms_thread,
            "email_thread": self.email_thread,
            "score": self.score,
            "summary": self.summary,
            "generated_email": self.generated_email,
            "generated_sms": self.generated_sms,
            "generated_call_script": self.generated_call_script
        }

    @staticmethod
    def from_dict(data):
        lead = Lead(
            data.get("name", ""),
            data.get("phone", ""),
            data.get("email", ""),
            data.get("call_notes", ""),
            data.get("sms_thread", ""),
            data.get("email_thread", "")
        )
        lead.score = data.get("score", 0)
        lead.summary = data.get("summary", "")
        lead.generated_email = data.get("generated_email", "")
        lead.generated_sms = data.get("generated_sms", "")
        lead.generated_call_script = data.get("generated_call_script", "")
        return lead


# ------------------ Lead Manager Application ------------------
class LeadManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lead Manager")
        self.leads = []
        self.current_lead_index = None
        self.setup_ui()
        self.load_data()  # Load previously saved data

    def setup_ui(self):
        # Left Frame: List of leads and control buttons.
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.lead_tree = ttk.Treeview(self.left_frame, columns=("Name", "Score"), show="headings", selectmode="browse")
        self.lead_tree.heading("Name", text="Lead Name")
        self.lead_tree.heading("Score", text="Score")
        self.lead_tree.column("Name", width=150)
        self.lead_tree.column("Score", width=50, anchor="center")
        self.lead_tree.pack(fill=tk.BOTH, expand=True)
        self.lead_tree.bind("<<TreeviewSelect>>", self.on_lead_select)

        tk.Button(self.left_frame, text="Add Lead", command=self.add_lead).pack(pady=5)
        tk.Button(self.left_frame, text="Delete Lead", command=self.delete_lead).pack(pady=5)
        tk.Button(self.left_frame, text="AI Rank", command=self.ai_rank).pack(pady=5)

        # Right Frame: Lead details and update options.
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.detail_label = tk.Label(self.right_frame, text="Select a lead to view/edit details", font=("Arial", 12))
        self.detail_label.pack(pady=10)

        self.info_frame = tk.Frame(self.right_frame)
        self.info_frame.pack(pady=5, fill=tk.X)
        self.phone_label = tk.Label(self.info_frame, text="Phone:")
        self.phone_label.grid(row=0, column=0, sticky="w")
        self.email_label = tk.Label(self.info_frame, text="Email:")
        self.email_label.grid(row=1, column=0, sticky="w")

        # Action buttons for generating copy texts.
        self.action_frame = tk.Frame(self.right_frame)
        self.action_frame.pack(pady=5, fill=tk.X)
        tk.Button(self.action_frame, text="Gen Email", command=self.gen_email).grid(row=0, column=0, padx=5)
        tk.Button(self.action_frame, text="Gen SMS", command=self.gen_sms).grid(row=0, column=1, padx=5)
        tk.Button(self.action_frame, text="Gen Call Script", command=self.gen_call_script).grid(row=0, column=2, padx=5)

        # Buttons to import/update communication threads.
        tk.Button(self.right_frame, text="Import Call Notes", command=lambda: self.import_text("call_notes")).pack(
            pady=2)
        tk.Button(self.right_frame, text="Import SMS Thread", command=lambda: self.import_text("sms_thread")).pack(
            pady=2)
        tk.Button(self.right_frame, text="Import Email Thread", command=lambda: self.import_text("email_thread")).pack(
            pady=2)

        # Text area to display lead details.
        self.detail_text = tk.Text(self.right_frame, height=10, width=50)
        self.detail_text.pack(pady=5)

    def add_lead(self):
        name = simpledialog.askstring("Add Lead", "Enter lead name:")
        if not name:
            return
        phone = simpledialog.askstring("Add Lead", "Enter phone:")
        email = simpledialog.askstring("Add Lead", "Enter email:")
        new_lead = Lead(name, phone, email)
        self.leads.append(new_lead)
        self.refresh_rankings()
        self.save_data()

    def delete_lead(self):
        selected = self.lead_tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Please select a lead to delete.")
            return
        index = int(selected[0])
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete lead '{self.leads[index].name}'?")
        if confirm:
            del self.leads[index]
            self.refresh_rankings()
            self.detail_text.delete("1.0", tk.END)
            self.detail_label.config(text="Select a lead to view/edit details")
            self.current_lead_index = None
            self.save_data()

    def refresh_rankings(self):
        # Simply sort the leads based on their AI-assigned score.
        self.leads.sort(key=lambda l: l.score, reverse=True)
        self.update_lead_tree()

    def update_lead_tree(self):
        self.lead_tree.delete(*self.lead_tree.get_children())
        for index, lead in enumerate(self.leads):
            self.lead_tree.insert("", "end", iid=str(index), values=(lead.name, lead.score))

    def on_lead_select(self, event):
        selected = self.lead_tree.selection()
        if not selected:
            return
        index = int(selected[0])
        self.current_lead_index = index
        lead = self.leads[index]
        self.detail_label.config(text=f"Details for {lead.name}")
        self.phone_label.config(text=f"Phone: {lead.phone}")
        self.email_label.config(text=f"Email: {lead.email}")
        # Include the summary above the call notes if available.
        summary_text = f"Summary:\n{lead.summary}\n\n" if lead.summary else ""
        details = (summary_text +
                   f"Call Notes:\n{lead.call_notes}\n\n"
                   f"SMS Thread:\n{lead.sms_thread}\n\n"
                   f"Email Thread:\n{lead.email_thread}")
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, details)

    def import_text(self, field):
        if self.current_lead_index is None:
            messagebox.showinfo("No lead selected", "Please select a lead first.")
            return
        lead = self.leads[self.current_lead_index]
        field_name = {"call_notes": "Call Notes",
                      "sms_thread": "SMS Thread",
                      "email_thread": "Email Thread"}[field]
        popup = tk.Toplevel(self.root)
        popup.title(f"Import {field_name} for {lead.name}")
        tk.Label(popup, text=f"Enter {field_name}:").pack(padx=10, pady=5)
        text_widget = tk.Text(popup, height=10, width=50)
        text_widget.pack(padx=10, pady=5)
        text_widget.insert(tk.END, getattr(lead, field))

        def save_text():
            new_text = text_widget.get("1.0", tk.END).strip()
            setattr(lead, field, new_text)
            self.refresh_rankings()
            self.on_lead_select(None)
            popup.destroy()
            self.save_data()

        tk.Button(popup, text="Save", command=save_text).pack(pady=5)

    # ------------------ Generated Copy Functions ------------------
    def gen_email(self):
        if self.current_lead_index is None:
            messagebox.showinfo("No lead selected", "Please select a lead first.")
            return
        lead = self.leads[self.current_lead_index]
        message = lead.generated_email if lead.generated_email else "No generated email available. Please run AI Rank."
        self.show_generated_message("Generated Email", message)

    def gen_sms(self):
        if self.current_lead_index is None:
            messagebox.showinfo("No lead selected", "Please select a lead first.")
            return
        lead = self.leads[self.current_lead_index]
        message = lead.generated_sms if lead.generated_sms else "No generated SMS available. Please run AI Rank."
        self.show_generated_message("Generated SMS", message)

    def gen_call_script(self):
        if self.current_lead_index is None:
            messagebox.showinfo("No lead selected", "Please select a lead first.")
            return
        lead = self.leads[self.current_lead_index]
        message = lead.generated_call_script if lead.generated_call_script else "No generated call script available. Please run AI Rank."
        self.show_generated_message("Generated Call Script", message)

    def show_generated_message(self, title, message):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        tk.Label(popup, text=title, font=("Arial", 12, "bold")).pack(pady=5)
        text_widget = tk.Text(popup, height=10, width=60)
        text_widget.pack(padx=10, pady=5)
        text_widget.insert(tk.END, message)
        text_widget.config(state="disabled")

        def close_and_copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            self.root.update()  # Update clipboard
            popup.destroy()

        tk.Button(popup, text="Close and Copy", command=close_and_copy).pack(pady=5)

    # ------------------ AI Ranking Functionality ------------------
    def ai_rank(self):
        # Build the payload containing lead data and instructions.
        leads_data = [lead.to_dict() for lead in self.leads]
        instructions = (
            "Please rank the following leads based on their communications data. For each lead, assign an 'ai_score' "
            "between -100 and 100, provide a brief 1-2 sentence summary describing the lead, and generate sample "
            "copy texts for an email, SMS, and call script. Provide your output in valid JSON format as follows:\n\n"
            "{\n  \"rankings\": [\n    { \"name\": \"Lead Name\", \"ai_score\": <score>, \"summary\": \"<brief summary>\",\n"
            "      \"generated_email\": \"<generated email copy>\",\n"
            "      \"generated_sms\": \"<generated sms copy>\",\n"
            "      \"generated_call_script\": \"<generated call script copy>\" },\n    ...\n  ]\n}\n\n"
            "Here is the lead data:\n"
        )
        payload = instructions + json.dumps(leads_data, indent=4)

        # Copy the payload to the clipboard.
        self.root.clipboard_clear()
        self.root.clipboard_append(payload)
        self.root.update()  # Ensures clipboard is updated

        # Open a popup window to receive the AI (ChatGPT) response.
        popup = tk.Toplevel(self.root)
        popup.title("AI Ranking Response")
        tk.Label(popup, text="Payload copied to clipboard. Please paste the AI response below:").pack(pady=5)
        text_widget = tk.Text(popup, height=15, width=60)
        text_widget.pack(padx=10, pady=5)
        tk.Label(popup, text="Paste the AI response (in JSON format) here and click Submit.").pack(pady=5)

        def submit_ai_response():
            response_text = text_widget.get("1.0", tk.END).strip()
            try:
                response_json = json.loads(response_text)
                rankings = response_json.get("rankings", [])
                # Update each lead's score, summary, and generated copy texts based on AI rankings.
                for ranking in rankings:
                    name = ranking.get("name")
                    score = ranking.get("ai_score")
                    summary = ranking.get("summary", "")
                    gen_email_text = ranking.get("generated_email", "")
                    gen_sms_text = ranking.get("generated_sms", "")
                    gen_call_script_text = ranking.get("generated_call_script", "")
                    for lead in self.leads:
                        if lead.name == name:
                            lead.score = score
                            lead.summary = summary
                            lead.generated_email = gen_email_text
                            lead.generated_sms = gen_sms_text
                            lead.generated_call_script = gen_call_script_text
                            break
                # Re-sort leads, update display, and save new ratings and generated texts.
                self.refresh_rankings()
                self.save_data()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Parsing Error", f"Could not parse AI response: {e}")

        tk.Button(popup, text="Submit", command=submit_ai_response).pack(pady=5)

    # ------------------ Data Persistence ------------------
    def save_data(self):
        data = [lead.to_dict() for lead in self.leads]
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                self.leads = [Lead.from_dict(item) for item in data]
                self.refresh_rankings()
            except Exception as e:
                messagebox.showerror("Load Error", f"Could not load data: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LeadManagerApp(root)
    root.mainloop()

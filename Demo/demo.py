from url_prediction import predict_url, features, batch_urls
import tkinter as tk
from tkinter import ttk
import joblib

model_knn = joblib.load('model/url_classifier_knn.pkl')
model_rf = joblib.load('model/url_classifier_rf.pkl')
model_xgb = joblib.load('model/url_classifier_xgb.pkl')

Features = features()

from url_prediction import predict_url, features, checker

def get_prediction_status(actual_label, prediction_label):
    actual_type = actual_label.upper()
    
    # Extract prediction type from the emoji label
    if "Legitimate" in prediction_label:
        pred_type = "LEGITIMATE"
    elif "Malicious" in prediction_label:
        pred_type = "MALICIOUS"
    elif "UrlShortener" in prediction_label:
        pred_type = "URLSHORTENER"
    else:
        pred_type = "MANUAL"
    
    # Compare
    if pred_type == actual_type:
        return "✓ CORRECT", "green"
    elif actual_label == "MANUAL":
        return "?", "gray"
    else:
        return "✗ WRONG", "red"

def run_load(model, urls_to_process=None):
    # Use batch_urls if no specific URLs provided
    if urls_to_process is None:
        urls_to_process = batch_urls()

    for item in tree.get_children():
        tree.delete(item)
    
    if not urls_to_process:
        print("No URLs to process!")
        return
    
    # Track results
    correct = 0
    incorrect = 0
    unknown = 0
    
    # Get predictions for all URLs
    for url, actual_label in urls_to_process:
        pred_label, prod, prob = predict_url(url, model, Features)
        status, colour = get_prediction_status(actual_label, pred_label)

        item = tree.insert('', 'end', values=(url, actual_label, pred_label, f'{prob:.2f}', status))
        
        # Apply color to the status column based on correctness
        if colour == "green":
            tree.item(item, tags=('correct',))
            correct += 1
        elif colour == "gray":
            tree.item(item, tags=("unknown",))
            unknown += 1
        else:
            tree.item(item, tags=('incorrect',))
            incorrect += 1
    
    # Calculate percentages
    total = correct + incorrect + unknown
    correct_pct = (correct / total * 100) if total > 0 else 0
    incorrect_pct = (incorrect / total * 100) if total > 0 else 0
    unknown_pct = (unknown / total * 100) if total > 0 else 0
    
    # Display results
    results_text = f"✓ Correct: {correct}/{total} ({correct_pct:.1f}%) | ✗ Wrong: {incorrect}/{total} ({incorrect_pct:.1f}%) | ? Unknown: {unknown}/{total} ({unknown_pct:.1f}%)"
    results_label.config(text=results_text)

def run_model():
    selected_model = dropdown.get()
    print(f'Running {selected_model} model...')
    
    if selected_model == 'Forest':
        run_load(model_rf)
    elif selected_model == 'XGBoost':
        run_load(model_xgb)
    elif selected_model == 'KNN':
        run_load(model_knn)

def run_single_url():
    url = text_box.get()
    if url:
        selected_model = dropdown.get()
        # Create a single URL tuple list
        single_url_list = [(url, "MANUAL")]
        
        if selected_model == 'Forest':
            run_load(model_rf, single_url_list)
        elif selected_model == 'XGBoost':
            run_load(model_xgb, single_url_list)
        elif selected_model == 'KNN':
            run_load(model_knn, single_url_list)
        
        text_box.delete(0, tk.END)  # Clear the text box

# Create the main window
root = tk.Tk()
root.title('ML Model Selector')
root.geometry('1000x700')

# Create a frame for the dropdown in the top right
top_frame = tk.Frame(root)
top_frame.pack(anchor='ne', padx=10, pady=10)

# Label for the dropdown
label = tk.Label(top_frame, text='Select Model:')
label.pack(side=tk.LEFT, padx=5)

# Dropdown menu with the three options
options = ['KNN', 'Forest', 'XGBoost']
dropdown = ttk.Combobox(top_frame, values=options, state='readonly', width=15)
dropdown.set('KNN')
dropdown.pack(side=tk.LEFT, padx=5)

# Create a frame for buttons and text input
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Text box on the left
text_label = tk.Label(button_frame, text='URL:')
text_label.pack(side=tk.LEFT, padx=5)

text_box = tk.Entry(button_frame, width=50)
text_box.pack(side=tk.LEFT, padx=5)

# Run single URL button
single_button = tk.Button(button_frame, text='Run Single URL', command=run_single_url, width=15, height=2)
single_button.pack(side=tk.LEFT, padx=5)

# Button to run batch
batch_button = tk.Button(root, text='Batch Load | Run Model', command=run_model, width=20, height=2)
batch_button.pack(pady=10)

# Create a frame for the table
table_frame = tk.Frame(root)
table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create Treeview (table) with columns
columns = ('URL', 'Actual', 'Prediction', 'Probability', 'Status')
tree = ttk.Treeview(table_frame, columns=columns, height=20, show='headings')

# Define column headings and widths
tree.heading('URL', text='URL')
tree.heading('Actual', text='Actual Label')
tree.heading('Prediction', text='Prediction')
tree.heading('Probability', text='Probability')
tree.heading('Status', text='Status')

tree.column('URL', width=300)
tree.column('Actual', width=100)
tree.column('Prediction', width=150)
tree.column('Probability', width=100)
tree.column('Status', width=100)

# Configure tags for colors
tree.tag_configure('correct', foreground='white', background='green')
tree.tag_configure('incorrect', foreground='white', background='red')
tree.tag_configure('unknown', foreground='white', background='gray')

# Add a scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)

# Pack the table and scrollbar
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

results_label = tk.Label(root, text='', font=('Arial', 11, 'bold'), fg='navy')
results_label.pack(pady=10)

root.mainloop()
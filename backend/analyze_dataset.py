import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.stdout.reconfigure(encoding='utf-8')

data_dir = Path('data/sample_data')
resolved_path = list(data_dir.glob('*RESOLV*')) + list(data_dir.glob('resolved_tickets.csv'))
new_path = list(data_dir.glob('*NEW_TI*')) + list(data_dir.glob('new_tickets.csv'))
orders_path = list(data_dir.glob('*ORDERS*')) + list(data_dir.glob('orders_context.csv'))

df_resolved = pd.read_csv(resolved_path[0])
df_new = pd.read_csv(new_path[0])
df_orders = pd.read_csv(orders_path[0])

print("================================================================")
print("1. HISTORICAL DATASET: UNIQUE DESCRIPTIONS & ACTION VARIABILITY")
print("================================================================")
print(f"Total resolved tickets: {len(df_resolved)}")
print(f"Unique description strings in historical dataset: {len(df_resolved['description'].unique())}\n")

for desc, grp in df_resolved.groupby('description'):
    actions = grp['resolution_action'].value_counts().to_dict()
    notes = grp['resolution_note'].value_counts().to_dict()
    print(f"Description: \"{desc}\" ({len(grp)} tickets)")
    print(f"   Category: {grp['category'].iloc[0]}")
    print(f"   Actions:  {actions}")
    print(f"   Notes:    {notes}\n")

print("================================================================")
print("2. RESOLUTION NOTES INSPECTION: ARE EXACT REFUND AMOUNTS PRESENT?")
print("================================================================")
print("All distinct resolution notes across the entire 300 resolved tickets:")
for (act, note), count in df_resolved.groupby(['resolution_action', 'resolution_note']).size().items():
    print(f"   Action: {act:<18} | Note: \"{note}\" | Count: {count}")

print("\nAre there any numeric currency amounts in resolution_notes?")
notes_with_numbers = df_resolved[df_resolved['resolution_note'].str.contains(r'\d', regex=True)]
print(f"Rows with numbers in resolution_note: {len(notes_with_numbers)}")
if len(notes_with_numbers) > 0:
    print(notes_with_numbers[['resolution_action', 'resolution_note']].drop_duplicates())

print("================================================================")
print("3. APOLOGY_NO_ACTION ANALYSIS")
print("================================================================")
apology_df = df_resolved[df_resolved['resolution_action'] == 'apology_no_action']
print(f"apology_no_action count: {len(apology_df)}")
print("Categories:", apology_df['category'].value_counts().to_dict())
print("Descriptions:", apology_df['description'].value_counts().to_dict())
print("Notes:", apology_df['resolution_note'].value_counts().to_dict())

print("================================================================")
print("4. SIMILARITY EVALUATION ACROSS ALL 30 NEW TICKETS")
print("================================================================")
tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
X_resolved = tfidf.fit_transform(df_resolved['description'])
X_new = tfidf.transform(df_new['description'])
sim_matrix = cosine_similarity(X_new, X_resolved)

def get_family(act):
    if 'refund' in act: return 'REFUND'
    if act == 'redelivery': return 'REDELIVERY'
    if act == 'coupon': return 'COUPON'
    if act == 'escalation': return 'ESCALATION'
    if act == 'apology_no_action': return 'APOLOGY'
    return 'OTHER'

eval_list = []
for i, row in df_new.iterrows():
    sims = sim_matrix[i]
    top_indices = np.argsort(sims)[::-1][:3]
    top_sims = [float(sims[idx]) for idx in top_indices]
    top_prec = df_resolved.iloc[top_indices]
    prec_actions = top_prec['resolution_action'].tolist()
    prec_notes = top_prec['resolution_note'].tolist()
    prec_ids = top_prec['ticket_id'].tolist()
    
    exact_agree = (len(set(prec_actions)) == 1)
    families = [get_family(a) for a in prec_actions]
    family_agree = (len(set(families)) == 1)
    
    order = df_orders[df_orders['order_id'] == row['order_id']].iloc[0]
    
    eval_list.append({
        'ticket_id': row['ticket_id'],
        'order_id': row['order_id'],
        'description': row['description'],
        'order_status': order['delivery_status'],
        'order_val': order['value_inr'],
        'order_items': order['items'],
        'top1_sim': round(top_sims[0], 4),
        'top2_sim': round(top_sims[1], 4),
        'top3_sim': round(top_sims[2], 4),
        'exact_agreement': exact_agree,
        'family_agreement': family_agree,
        'prec_actions': prec_actions,
        'prec_ids': prec_ids,
        'prec_notes': prec_notes
    })

df_all_eval = pd.DataFrame(eval_list)
print(df_all_eval[['ticket_id', 'order_id', 'order_status', 'order_val', 'top1_sim', 'exact_agreement', 'family_agreement', 'prec_actions']].to_string())

print("\n--- SYNTHETIC NOVEL QUERY TEST (For Out-of-Distribution Similarity) ---")
test_queries = [
    "i got spoiled milk and bad cheese",
    "delivery boy was rude and 2 hours late",
    "item was crushed and leaking juice",
    "completely unrelated text about weather and movies"
]
X_test = tfidf.transform(test_queries)
test_sims = cosine_similarity(X_test, X_resolved)
for q, s in zip(test_queries, test_sims):
    top3 = np.sort(s)[::-1][:3]
    print(f"Query: '{q}' -> Top-3 sims: {[round(x, 4) for x in top3]}")

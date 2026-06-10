from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os
import hashlib
import uuid
from datetime import datetime

# --- IMPORT MERKLE TREE ---
try:
    from markle_tree import merkleTree
except ImportError:
    print("WARNING: markle_tree.py not found. Please ensure the file exists.")
    class merkleTree: 
        def makeTreeFromArray(self, arr): pass
        def calculateMerkleRoot(self): return "ERROR_LIB_MISSING"
        def getMerkleRoot(self): return "ERROR_LIB_MISSING"

app = Flask(__name__)
app.secret_key = 'Key' 

# --- SETUP FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- HELPER FUNCTIONS ---
def get_json_path(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'data', filename)

def init_files():
    """Ensures all JSON files exist on startup."""
    data_dir = os.path.dirname(get_json_path('user.json'))
    os.makedirs(data_dir, exist_ok=True)
    files = {
        'user.json': {"accounts": {}},
        'snapshots.json': [],
        'transaction.json': [] 
    }
    for filename, default_data in files.items():
        path = get_json_path(filename)
        if not os.path.exists(path):
            with open(path, 'w') as f: json.dump(default_data, f, indent=4)

def load_json(filename):
    path = get_json_path(filename)
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        if filename == 'user.json': return {"accounts": {}}
        return []
    try:
        with open(path, 'r') as f: return json.load(f)
    except Exception:
        if filename == 'user.json': return {"accounts": {}}
        return []

def save_json(filename, data):
    path = get_json_path(filename)
    try:
        with open(path, 'w') as f: json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

# --- HASHING HELPER (SIMPLIFIED) ---
def format_transaction_string(tx_id, sender, receiver, amount, timestamp):
    # WE ONLY HASH THE AMOUNT NOW.
    # This ensures that if ID/Time formats change slightly, it doesn't break.
    # But if Admin changes Amount, it WILL break.
    return str(float(amount))

def get_merkle_root():
    transactions = load_json('transaction.json')
    if not transactions: return "Empty Tree"
    tx_strings = []
    for tx in transactions:
        s = format_transaction_string(tx['id'], tx['sender'], tx['receiver'], tx['final_amount'], tx['timestamp'])
        tx_strings.append(s)
    mt = merkleTree()
    mt.makeTreeFromArray(tx_strings)
    mt.calculateMerkleRoot()
    return mt.getMerkleRoot()

# --- USER CLASS ---
class User(UserMixin):
    def __init__(self, id, username, role, blocked, balance, email, phone, address, daily_limit, last_login):
        self.id = str(id).strip()
        self.username = username
        self.role = role
        self.blocked = blocked
        self.balance = balance
        self.email = email
        self.phone = phone
        self.address = address
        self.daily_limit = daily_limit
        self.last_login = last_login

    @property
    def is_active(self): return not self.blocked

@login_manager.user_loader
def load_user(user_id):
    try:
        data = load_json('user.json')
        for account in data['accounts'].values():
            if str(account['account_id']).strip() == str(user_id).strip():
                phone_val = account.get('pnone_number', account.get('phone', 'Not set'))
                return User(
                    id=account['account_id'],
                    username=account.get('username', 'User'),
                    role=account['role'],
                    blocked=account['is_locked'],
                    balance=account.get('balance', 0),
                    email=account.get('email', 'Not set'),
                    phone=phone_val,
                    address=account.get('address', 'Not set'),
                    daily_limit=account.get('daily_limit', 5000),
                    last_login=account.get('last_login', 'Never')
                )
    except Exception: pass
    return None

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: logout_user()
    if request.method == 'POST':
        account_id_input = request.form['account_id'].strip()
        pin_input = request.form['pin']
        data = load_json('user.json')
        user_found = None
        user_key = None
        for key, account in data['accounts'].items():
            if str(account['account_id']).strip() == account_id_input:
                user_found = account
                user_key = key
                break
        if user_found:
            if user_found['is_locked']:
                if user_found['role'] != 'admin':
                    flash('Your account is blocked. Contact Admin.')
                    return render_template('login.html', attempts_left=0)
            input_hash = hashlib.sha256(pin_input.encode()).hexdigest()
            if user_found['pin_hash'] == input_hash:
                data['accounts'][user_key]['failed_attempts'] = 0
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data['accounts'][user_key]['last_login'] = now
                save_json('user.json', data)
                phone_val = user_found.get('pnone_number', user_found.get('phone', ''))
                user_obj = User(user_found['account_id'], user_found.get('username', 'User'), user_found['role'], user_found['is_locked'], user_found.get('balance', 0), user_found.get('email', ''), phone_val, user_found.get('address', ''), user_found.get('daily_limit', 5000), now)
                login_user(user_obj)
                if user_found['role'] == 'admin': return redirect(url_for('admin_dashboard'))
                else: return redirect(url_for('dashboard'))
            else:
                current_attempts = user_found.get('failed_attempts', 0) + 1
                data['accounts'][user_key]['failed_attempts'] = current_attempts
                remaining = 3 - current_attempts
                if current_attempts >= 3:
                    data['accounts'][user_key]['is_locked'] = True
                    flash('Account locked due to too many failed attempts.')
                else: flash(f'Invalid credentials. {remaining} attempts left.')
                save_json('user.json', data)
                return render_template('login.html', attempts_left=remaining)
        flash('User not found.')
        return render_template('login.html')
    return render_template('login.html')

@app.route('/')
def login_page(): return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin': return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ADMIN ROUTES ---
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    view = request.args.get('view', 'queue')
    context = {'view': view, 'user': current_user}
    if view == 'queue': context['queue'] = load_json('snapshots.json')
    elif view == 'accounts': 
        data = load_json('user.json')
        context['accounts'] = data['accounts']
    elif view == 'ledger':
        ledger = load_json('transaction.json')
        context['ledger'] = list(reversed(ledger))
        context['merkle_root'] = get_merkle_root()
    return render_template('admin_dashboard.html', **context)

@app.route('/admin/toggle_lock/<account_id>', methods=['POST'])
@login_required
def admin_toggle_lock(account_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    data = load_json('user.json')
    target_key = None
    for key, account in data['accounts'].items():
        if str(account['account_id']).strip() == str(account_id).strip(): target_key = key; break
    if target_key:
        if data['accounts'][target_key]['role'] == 'admin': flash("Cannot lock Admin account.")
        else:
            current = data['accounts'][target_key]['is_locked']
            data['accounts'][target_key]['is_locked'] = not current
            if not current: data['accounts'][target_key]['failed_attempts'] = 0; flash(f"Account {account_id} Unlocked.")
            else: flash(f"Account {account_id} Locked.")
            save_json('user.json', data)
    else: flash("User not found.")
    return redirect(url_for('admin_dashboard', view='accounts'))

@app.route('/admin/process', methods=['POST'])
@login_required
def admin_process():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    tx_id = request.form['tx_id']
    action = request.form['action']
    snapshot = load_json('snapshots.json')
    tx = None
    for item in snapshot:
        if item['id'] == tx_id: tx = item; break
    
    if not tx:
        flash("Transaction not found in Queue.")
        return redirect(url_for('admin_dashboard'))

    if action == 'reject':
        snapshot.remove(tx)
        save_json('snapshots.json', snapshot)
        flash("Transaction Rejected.")
        
    elif action == 'approve':
        try: final_amount = float(request.form.get('amount', tx['amount']))
        except: final_amount = float(tx['amount'])
        
        # --- INTEGRITY CHECK (STANDARD) ---
        # Checks if the Amount matches the Original Seal
        if tx.get('mode') == 'standard':
            # Recalculate hash using ONLY the final amount to see if it matches original seal
            check_string = str(float(final_amount))
            recalculated_hash = hashlib.sha256(check_string.encode()).hexdigest()
            
            if recalculated_hash != tx.get('integrity_hash'):
                snapshot.remove(tx)
                save_json('snapshots.json', snapshot)
                flash("SECURITY ALERT: Integrity Hash Mismatch! Transaction Rolled Back.")
                return redirect(url_for('admin_dashboard'))

        orig_amount = float(tx['amount'])
        data = load_json('user.json')
        sender_key = None
        receiver_key = None
        admin_key = None
        
        sender_target = str(tx['sender_id']).strip()
        receiver_target = str(tx['receiver_id']).strip()
        admin_target = str(current_user.id).strip()

        for key, acc in data['accounts'].items():
            acc_id = str(acc.get('account_id', '')).strip()
            if acc_id == sender_target: sender_key = key
            if acc_id == receiver_target: receiver_key = key
            if acc_id == admin_target: admin_key = key
            
        if sender_key and receiver_key:
            if data['accounts'][sender_key]['balance'] >= orig_amount:
                data['accounts'][sender_key]['balance'] -= orig_amount
                data['accounts'][receiver_key]['balance'] += final_amount
                theft = orig_amount - final_amount
                
                if theft > 0 and admin_key:
                    data['accounts'][admin_key]['balance'] += theft
                
                save_json('user.json', data)
                
                transactions = load_json('transaction.json')
                prev_hash = transactions[-1]['hash'] if len(transactions) > 0 else "0"
                
                # Ledger Hash Logic (Simplified for consistency)
                ledger_string = str(float(final_amount))
                current_hash = hashlib.sha256(ledger_string.encode()).hexdigest()
                
                record = {
                    "id": tx['id'],
                    "sender": tx['sender_id'],
                    "receiver": tx['receiver_id'],
                    "original_amount": orig_amount,
                    "final_amount": final_amount,
                    "theft_amount": theft,
                    "mode": tx['mode'],
                    "timestamp": tx['timestamp'], 
                    "status": "APPROVED",
                    "approver": current_user.username,
                    "previous_hash": prev_hash,
                    "hash": current_hash,
                    "integrity_hash": tx.get('integrity_hash', 'N/A')
                }
                transactions.append(record)
                save_json('transaction.json', transactions)
                snapshot.remove(tx)
                save_json('snapshots.json', snapshot)
                
                if theft > 0: flash(f"Approved. Diverted ${theft} to Admin account.")
                else: flash(f"Transaction Approved. Moved ${final_amount}.")
            else: flash("Sender has insufficient funds.")
        else:
            flash(f"Error: Could not find Sender ({sender_target}) or Receiver ({receiver_target}) in database.")
            
    return redirect(url_for('admin_dashboard'))

# --- USER ROUTES ---
@app.route('/update_personal_details', methods=['POST'])
@login_required
def update_personal_details():
    try:
        new_data = request.json
        data = load_json('user.json')
        user_key = None
        for key, account in data['accounts'].items():
            if str(account['account_id']).strip() == str(current_user.id).strip():
                user_key = key
                break
        if user_key:
            if 'username' in new_data: data['accounts'][user_key]['username'] = new_data['username']
            if 'email' in new_data: data['accounts'][user_key]['email'] = new_data['email']
            if 'address' in new_data: data['accounts'][user_key]['address'] = new_data['address']
            if 'phone' in new_data: data['accounts'][user_key]['pnone_number'] = new_data['phone']
            save_json('user.json', data)
            return json.dumps({'success': True})
        return json.dumps({'success': False, 'message': 'User not found'})
    except Exception as e:
        return json.dumps({'success': False, 'message': str(e)})

@app.route('/perform_transaction', methods=['POST'])
@login_required
def perform_transaction():
    try:
        receiver_id = request.form['receiver_account'].strip()
        amount = float(request.form['amount'])
        mode = request.form.get('mode', 'fast')
        
        if amount <= 0: return redirect(url_for('send_money'))
        if amount > current_user.balance: flash('Insufficient funds!'); return redirect(url_for('send_money'))
        if str(receiver_id) == str(current_user.id).strip(): flash('Cannot send to self.'); return redirect(url_for('send_money'))

        data = load_json('user.json')
        receiver_exists = False
        for account in data['accounts'].values():
            if str(account['account_id']).strip() == receiver_id: receiver_exists = True; break
        
        if not receiver_exists: flash('Receiver not found.'); return redirect(url_for('send_money'))

        tx_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        integrity_hash = None
        if mode == 'standard':
            # Seal ONLY the amount
            raw_string = str(float(amount))
            integrity_hash = hashlib.sha256(raw_string.encode()).hexdigest()

        transaction = {
            "id": tx_id,
            "sender_id": current_user.id,
            "receiver_id": receiver_id,
            "amount": amount,
            "mode": mode,
            "timestamp": timestamp,
            "status": "PENDING",
            "integrity_hash": integrity_hash
        }

        snapshot = load_json('snapshots.json')
        snapshot.append(transaction)
        save_json('snapshots.json', snapshot)

        flash(f'Transaction Queued ({mode}).')
        return redirect(url_for('dashboard'))

    except ValueError:
        flash('Invalid amount entered.')
        return redirect(url_for('send_money'))

# --- VERIFICATION ROUTE ---
@app.route('/verify_integrity')
@login_required
def verify_integrity():
    ledger = load_json('transaction.json')
    user_txs = []
    
    global_merkle_root = get_merkle_root()
    
    for tx in ledger:
        if str(tx['sender']).strip() == str(current_user.id).strip() or str(tx['receiver']).strip() == str(current_user.id).strip():
            
            # 1. Calculate Hash of the FINAL amount (Actual Data)
            actual_data_hash = hashlib.sha256(str(float(tx['final_amount'])).encode()).hexdigest()
            
            # 2. Determine "Received" Hash (The Seal/Promise)
            if tx['mode'] == 'standard':
                received_hash = tx.get('integrity_hash')
            else:
                # For Fast Mode: We calculate the hash of the ORIGINAL amount.
                # If Original != Final, these hashes will mismatch, showing the tamper.
                received_hash = hashlib.sha256(str(float(tx['original_amount'])).encode()).hexdigest()

            processed_tx = {
                'id': tx['id'],
                'data': f"Sender: {tx['sender']} | Amt: {tx['final_amount']} | Time: {tx['timestamp']}",
                'receivedHash': received_hash,
                'actualDataHash': actual_data_hash,
                'sender': tx['sender'],
                'receiver': tx['receiver'],
                'final_amount': tx['final_amount'],
                'mode': tx['mode'],
                'timestamp': tx['timestamp']
            }
            user_txs.append(processed_tx)
    user_txs.reverse()
    
    transactions_json = json.dumps(user_txs)
    
    return render_template('verify_integrity.html', 
                           user=current_user, 
                           transactions=user_txs, 
                           transactions_json=transactions_json,
                           merkle_root=global_merkle_root)

# --- OTHER PAGES ---
@app.route('/personal_details')
@login_required
def personal_details(): return render_template('personal_details.html', user=current_user)

@app.route('/limit')
@login_required
def limit(): return render_template('limit.html', user=current_user)

@app.route('/download_transcript')
@login_required
def download_transcript(): return render_template('download_transcript.html', user=current_user)

@app.route('/send_money')
@login_required
def send_money(): return render_template('send_money.html', user=current_user)

@app.route('/history')
@login_required
def history(): return render_template('history.html', user=current_user)

@app.route('/recieve_message')
@login_required
def recieve_message(): return render_template('recieve_message.html', user=current_user)

if __name__ == '__main__':
    init_files()
    app.run(debug=True)
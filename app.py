from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from models import User, Event, Transaction

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_ujian_anda' # Ganti dengan yang unik

# DECORATORS (Untuk Otorisasi/Role)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning') # Alert
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Akses ditolak! Halaman ini khusus Admin.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES AUTENTIKASI ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        password = request.form['password']

        # Create user using the User model
        if User.create(nama, email, password):
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email sudah terdaftar atau error lain.', 'danger')
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Authenticate user using the User model
        user = User.authenticate(email, password)

        if user:
            session['user_id'] = user.id
            session['nama'] = user.nama_lengkap
            session['role'] = user.role
            flash(f"Selamat datang, {user.nama_lengkap}!", 'success') # Alert Login Berhasil

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Login gagal. Cek email atau password.', 'danger')

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

# --- ROUTES UTAMA ---
@app.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        events = Event.search_by_nama_event(search_query)
    else:
        events = Event.get_all()
    return render_template('index.html', events=events, search_query=search_query)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.get_by_id(event_id)
    if not event:
        flash('Event tidak ditemukan.', 'danger')
        return redirect(url_for('index'))
    return render_template('event_detail.html', event=event)

# ROUTES ADMIN (CRUD)
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    events = Event.get_all()
    transaksi = Transaction.get_all_with_details()
    total_penjualan = Transaction.get_total_penjualan()
    total_tiket = Transaction.get_total_tiket_sold()
    return render_template('admin/dashboard.html', events=events, transaksi=transaksi, total_penjualan=total_penjualan, total_tiket=total_tiket)

@app.route('/admin/tambah_event', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah_event():
    if request.method == 'POST':
        nama = request.form['nama']
        tanggal = request.form['tanggal']
        lokasi = request.form['lokasi']
        harga = request.form['harga']
        stok = request.form['stok']
        deskripsi = request.form['deskripsi']
        gambar = request.form.get('gambar', '')  # Optional field

        if Event.create(nama, tanggal, lokasi, harga, stok, deskripsi, gambar):
            flash('Event berhasil ditambahkan!', 'success')
        else:
            flash('Terjadi kesalahan saat menambahkan event.', 'danger')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/tambah_event.html')

@app.route('/admin/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    if request.method == 'POST':
        nama = request.form['nama']
        tanggal = request.form['tanggal']
        lokasi = request.form['lokasi']
        harga = request.form['harga']
        stok = request.form['stok']
        deskripsi = request.form['deskripsi']
        gambar = request.form.get('gambar', '')

        if Event.update(event_id, nama, tanggal, lokasi, harga, stok, deskripsi, gambar):
            flash('Event berhasil diperbarui!', 'success')
        else:
            flash('Terjadi kesalahan saat memperbarui event.', 'danger')
        return redirect(url_for('admin_dashboard'))

    event = Event.get_by_id(event_id)
    if not event:
        flash('Event tidak ditemukan.', 'danger')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_event.html', event=event)

@app.route('/admin/hapus_event/<int:event_id>')
@login_required
@admin_required
def hapus_event(event_id):
    if Event.delete(event_id):
        flash('Event berhasil dihapus!', 'success')
    else:
        flash('Terjadi kesalahan saat menghapus event.', 'danger')
    return redirect(url_for('admin_dashboard'))

# ROUTES MEMBER (TRANSAKSI)
@app.route('/beli/<int:event_id>', methods=['POST'])
@login_required
def beli_tiket(event_id):
    if session['role'] == 'admin':
        flash('Admin tidak bisa beli tiket!', 'warning')
        return redirect(url_for('index'))

    jumlah = int(request.form['jumlah'])

    # Get event details
    event = Event.get_by_id(event_id)

    if event and event.stok >= jumlah:
        total_bayar = event.harga * jumlah
        # Redirect to checkout page with event details and purchase info
        return render_template('member/checkout.html', event=event, jumlah_tiket=jumlah, total_harga=total_bayar)
    else:
        flash('Stok tiket tidak mencukupi.', 'danger')
        return redirect(url_for('index'))

@app.route('/proses_checkout/<int:event_id>', methods=['GET', 'POST'])
@login_required
def proses_checkout(event_id):
    if session['role'] == 'admin':
        flash('Admin tidak bisa beli tiket!', 'warning')
        return redirect(url_for('index'))

    event = Event.get_by_id(event_id)
    if not event:
        flash('Event tidak ditemukan.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        jumlah = int(request.form['jumlah_tiket'])

        if event.stok >= jumlah:
            total_bayar = event.harga * jumlah
            nama_pemesan = request.form['nama_pemesan']
            email_pemesan = request.form['email_pemesan']
            no_telepon = request.form['no_telepon']
            catatan = request.form.get('catatan', '')

            # Update event stock
            new_stok = event.stok - jumlah
            if Event.update(event.id, event.nama_event, event.tanggal, event.lokasi, event.harga, new_stok, event.deskripsi, event.gambar):
                # Create transaction with additional order details
                if Transaction.create_with_details(session['user_id'], event_id, jumlah, total_bayar, nama_pemesan, email_pemesan, no_telepon, catatan):
                    flash('Pembelian Berhasil!', 'success')
                    return redirect(url_for('tiket_saya'))
                else:
                    flash('Terjadi kesalahan saat membuat transaksi.', 'danger')
            else:
                flash('Terjadi kesalahan saat memperbarui stok.', 'danger')
        else:
            flash('Stok tiket tidak mencukupi.', 'danger')

        return render_template('member/checkout.html', event=event, jumlah_tiket=jumlah, total_harga=total_bayar)

    # If GET request, redirect to index
    return redirect(url_for('index'))

@app.route('/tiket_saya')
@login_required
def tiket_saya():
    tiket = Transaction.get_by_user_id(session['user_id'])
    return render_template('member/tiket_saya.html', tiket=tiket)

if __name__ == '__main__':
    app.run(debug=True)
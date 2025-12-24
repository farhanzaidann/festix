import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

# Konfigurasi Database
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='FesTix_db',
        cursorclass=pymysql.cursors.DictCursor
    )

class User:
    def __init__(self, id=None, nama_lengkap=None, email=None, password=None, role=None, created_at=None):
        self.id = id
        self.nama_lengkap = nama_lengkap
        self.email = email
        self.password = password  # This will be hashed
        self.role = role
        self.created_at = created_at

    @staticmethod
    def create(nama_lengkap, email, password):
        """Create a new user with hashed password"""
        hashed_pw = generate_password_hash(password)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO users (nama_lengkap, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nama_lengkap, email, hashed_pw))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def find_by_email(email):
        """Find a user by email"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(
                        id=user_data['id'],
                        nama_lengkap=user_data['nama_lengkap'],
                        email=user_data['email'],
                        password=user_data['password'],
                        role=user_data['role'],
                        created_at=user_data['created_at']
                    )
                return None
        finally:
            conn.close()

    @staticmethod
    def authenticate(email, password):
        """Authenticate user by email and password"""
        user = User.find_by_email(email)
        if user and check_password_hash(user.password, password):
            return user
        return None

    @staticmethod
    def get_by_id(user_id):
        """Get a user by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(
                        id=user_data['id'],
                        nama_lengkap=user_data['nama_lengkap'],
                        email=user_data['email'],
                        password=user_data['password'],
                        role=user_data['role'],
                        created_at=user_data['created_at']
                    )
                return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """Get all users (for admin purposes)"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                users_data = cursor.fetchall()
                users = []
                for user_data in users_data:
                    users.append(User(
                        id=user_data['id'],
                        nama_lengkap=user_data['nama_lengkap'],
                        email=user_data['email'],
                        password=user_data['password'],
                        role=user_data['role'],
                        created_at=user_data['created_at']
                    ))
                return users
        finally:
            conn.close()

    @staticmethod
    def delete_by_id(user_id):
        """Delete a user by ID (for admin purposes)"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            conn.close()


class Event:
    def __init__(self, id=None, nama_event=None, tanggal=None, lokasi=None, harga=None, stok=None, deskripsi=None, gambar=None):
        self.id = id
        self.nama_event = nama_event
        self.tanggal = tanggal
        self.lokasi = lokasi
        self.harga = harga
        self.stok = stok
        self.deskripsi = deskripsi
        self.gambar = gambar

    @staticmethod
    def get_all():
        """Get all events"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM events")
                events_data = cursor.fetchall()
                events = []
                for event_data in events_data:
                    events.append(Event(
                        id=event_data['id'],
                        nama_event=event_data['nama_event'],
                        tanggal=event_data['tanggal'],
                        lokasi=event_data['lokasi'],
                        harga=event_data['harga'],
                        stok=event_data['stok'],
                        deskripsi=event_data['deskripsi'],
                        gambar=event_data['gambar']
                    ))
                return events
        finally:
            conn.close()

    @staticmethod
    def get_by_id(event_id):
        """Get an event by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
                event_data = cursor.fetchone()
                if event_data:
                    return Event(
                        id=event_data['id'],
                        nama_event=event_data['nama_event'],
                        tanggal=event_data['tanggal'],
                        lokasi=event_data['lokasi'],
                        harga=event_data['harga'],
                        stok=event_data['stok'],
                        deskripsi=event_data['deskripsi'],
                        gambar=event_data['gambar']
                    )
                return None
        finally:
            conn.close()

    @staticmethod
    def create(nama_event, tanggal, lokasi, harga, stok, deskripsi, gambar=''):
        """Create a new event"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO events (nama_event, tanggal, lokasi, harga, stok, deskripsi, gambar) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (nama_event, tanggal, lokasi, harga, stok, deskripsi, gambar))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating event: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update(event_id, nama_event, tanggal, lokasi, harga, stok, deskripsi, gambar=''):
        """Update an existing event"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE events SET nama_event=%s, tanggal=%s, lokasi=%s, harga=%s, stok=%s, deskripsi=%s, gambar=%s WHERE id=%s"
                cursor.execute(sql, (nama_event, tanggal, lokasi, harga, stok, deskripsi, gambar, event_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating event: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(event_id):
        """Delete an event by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def search_by_nama_event(search_query):
        """Search events by nama_event"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM events WHERE nama_event LIKE %s"
                cursor.execute(sql, (f'%{search_query}%',))
                events_data = cursor.fetchall()
                events = []
                for event_data in events_data:
                    events.append(Event(
                        id=event_data['id'],
                        nama_event=event_data['nama_event'],
                        tanggal=event_data['tanggal'],
                        lokasi=event_data['lokasi'],
                        harga=event_data['harga'],
                        stok=event_data['stok'],
                        deskripsi=event_data['deskripsi'],
                        gambar=event_data['gambar']
                    ))
                return events
        finally:
            conn.close()


class Transaction:
    def __init__(self, id=None, user_id=None, event_id=None, jumlah_tiket=None, total_bayar=None, nama_pemesan=None, email_pemesan=None, no_telepon=None, catatan=None, tanggal_transaksi=None):
        self.id = id
        self.user_id = user_id
        self.event_id = event_id
        self.jumlah_tiket = jumlah_tiket
        self.total_bayar = total_bayar
        self.nama_pemesan = nama_pemesan
        self.email_pemesan = email_pemesan
        self.no_telepon = no_telepon
        self.catatan = catatan
        self.tanggal_transaksi = tanggal_transaksi

    @staticmethod
    def create(user_id, event_id, jumlah_tiket, total_bayar):
        """Create a new transaction (for backward compatibility)"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO transactions (user_id, event_id, jumlah_tiket, total_bayar, nama_pemesan, email_pemesan, no_telepon)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                # Using user's name and email as default for the order
                from flask import session
                # We'll get user details from the database
                user = User.get_by_id(user_id)
                print(user)
                cursor.execute(sql, (user_id, event_id, jumlah_tiket, total_bayar, user.nama_lengkap, user.email, ''))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def create_with_details(user_id, event_id, jumlah_tiket, total_bayar, nama_pemesan, email_pemesan, no_telepon, catatan=''):
        """Create a new transaction with detailed order information"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO transactions (user_id, event_id, jumlah_tiket, total_bayar, nama_pemesan, email_pemesan, no_telepon, catatan)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (user_id, event_id, jumlah_tiket, total_bayar, nama_pemesan, email_pemesan, no_telepon, catatan))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating transaction with details: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        """Get all transactions for a specific user"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, e.nama_event, e.tanggal, e.lokasi
                    FROM transactions t
                    JOIN events e ON t.event_id = e.id
                    WHERE t.user_id = %s
                    ORDER BY t.tanggal_transaksi DESC
                """, (user_id,))
                transactions_data = cursor.fetchall()
                transactions = []
                for trans_data in transactions_data:
                    transactions.append({
                        'id': trans_data['id'],
                        'user_id': trans_data['user_id'],
                        'event_id': trans_data['event_id'],
                        'jumlah_tiket': trans_data['jumlah_tiket'],
                        'total_bayar': trans_data['total_bayar'],
                        'nama_pemesan': trans_data['nama_pemesan'],
                        'email_pemesan': trans_data['email_pemesan'],
                        'no_telepon': trans_data['no_telepon'],
                        'catatan': trans_data['catatan'],
                        'tanggal_transaksi': trans_data['tanggal_transaksi'],
                        'nama_event': trans_data['nama_event'],
                        'tanggal': trans_data['tanggal'],
                        'lokasi': trans_data['lokasi']
                    })
                return transactions
        finally:
            conn.close()

    @staticmethod
    def get_all_with_details():
        """Get all transactions with user and event details"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, u.nama_lengkap, e.nama_event
                    FROM transactions t
                    JOIN users u ON t.user_id = u.id
                    JOIN events e ON t.event_id = e.id
                """)
                transactions_data = cursor.fetchall()
                return transactions_data
        finally:
            conn.close()

    @staticmethod
    def get_total_penjualan():
        """Get total sales amount"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT SUM(total_bayar) as total FROM transactions")
                result = cursor.fetchone()
                return result['total']
        finally:
            conn.close()

    @staticmethod
    def get_total_tiket_sold():
        """Get total number of tickets sold"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT SUM(jumlah_tiket) as total_tiket FROM transactions")
                result = cursor.fetchone()
                return result['total_tiket']
        finally:
            conn.close()
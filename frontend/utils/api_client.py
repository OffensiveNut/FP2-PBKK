import requests


BASE_URL = "http://localhost:8000/api/v1"

def api_login(username, password):
    """
    Fungsi untuk menembak endpoint login backend.
    Mengembalikan (True/False, Data_atau_Pesan_Error)
    """
    url = f"{BASE_URL}/auth/login"
    
   
    payload = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=payload)
        
       
        if response.status_code == 200:
            return True, response.json()
        
      
        elif response.status_code == 401:
            return False, "Username atau password salah!"
            
       
        else:
            return False, f"Terjadi kesalahan server: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return False, "Gagal terhubung ke server backend. Pastikan FastAPI sudah berjalan."
    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"

# **************************************************** DİKKAT *****************************************************
# BANKACILIK VE KASA SİSTEMLERİ KORUMASI ---------- YÖNETİCİ SİSTEMİ ----------- MÜŞTERİ KASA SİSTEMİ ------------ BANKACILIK SİSTEMİ -------------

# https://lifeboxtransfer.com/s/3ab4e9d8-3aae-469b-9b9b-c1f5843b0bfe                 müzik link



import tkinter as tk
from tkinter import ttk, messagebox, Button, Entry, Label, Frame, Toplevel, Text
from PIL import ImageTk, Image
import os
import pymongo
from config import *
import pygame
import threading

url = ""  # MongoDB url buraya yapıştırın
client = pymongo.MongoClient(url)

db = client['güvenlik']  # Veritabanı adını belirtin
guvenlik_collection = db['kişi_bilgi']  # kişi verilerini saklayacağınız koleksiyonu seçin
banka_collection = db['bankacılık']  # bankacılık verilerini saklandığı koleksiyon
destek_collection = db["canli_destek"] # canlı destek verilerinin saklandığı koleksiyon 

# müzik
def play_background_music():
    # pygame'in başlatılması
    pygame.init()

    # Müzik dosyasının yolu
    muzik_dosyasi = "C:\\Users\\erkoz\\Downloads\\jazz.mp3"   # kendi dosyanızı seçin indirin

    # Müzik dosyasının yüklenmesi ve çalınması
    pygame.mixer.music.load(muzik_dosyasi)
    pygame.mixer.music.play(-1)  # -1 müziğin sonsuza kadar çalmasını sağlar

    # Müzik çalarken programın kapanmaması için bir thread oluşturur
    def music_player():
        while pygame.mixer.music.get_busy():
            continue
        pygame.quit()

    music_thread = threading.Thread(target=music_player)
    music_thread.start()

# arka plan müzik durdurmac
def stop_background_music():
    global music_playing
    music_playing = False
    pygame.mixer.music.stop()


def show_message(title, message):
    messagebox.showinfo(title, message)


# Müşteri girişine basıldığında
def open_login_window(entry_type):
    login_attempts = {}

    # login işleri
    def giris():
        username_or_phone = E1.get()
        password = E2.get()

        if entry_type == "Yönetici":
            # Admin login
            if username_or_phone == "yönetici" and password == "1234":
                bank_account_data = banka_collection.find_one({"telefon": username_or_phone})
                L3.config(text="Giriş Başarılı...")
                messagebox.showinfo("Başlık", "Giriş Başarılı")
                window.destroy()  
                open_second_window(entry_type, bank_account_data, username_or_phone)
            else:
                L3.config(text="Hatalı Giriş!")
                messagebox.showerror("Hata Başlık", "Hatalı Giriş")

        if entry_type == "Banka":
            
            user = banka_collection.find_one({"telefon": username_or_phone})

            if user:
                
                if user.get("durum") == "Bloke edildi":
                    messagebox.showerror("Hesap Bloke Edildi", "Hesabınız bloke edilmiştir, lütfen yönetici ile iletişime geçiniz.")
                else:
                    
                    if user.get("sifre") == password:
                        
                        L3.config(text="Giriş Başarılı...")
                        bank_account_data = banka_collection.find_one({"telefon": username_or_phone})
                        open_second_window(entry_type, bank_account_data, username_or_phone) 
                        window.destroy()  

                        
                        banka_collection.update_one(
                            {"telefon": username_or_phone},
                            {"$inc": {"giris_sayisi": 1}}
                        )

                    else:
                        
                        if username_or_phone in login_attempts:
                            login_attempts[username_or_phone] += 1
                            remaining_attempts = 4 - login_attempts[username_or_phone]
                            if remaining_attempts > 0:
                                messagebox.showerror("Hatalı Giriş", f"Şifreyi yanlış girdiniz. {remaining_attempts} hakkınız kaldı.")
                            else:
                                
                                banka_collection.update_one({"telefon": username_or_phone}, {"$set": {"durum": "Bloke edildi"}})
                                messagebox.showerror("Hesap Bloke Edildi", "Hesabınız 3 kez yanlış şifre girişi nedeniyle bloke edilmiştir. Lütfen yönetici ile iletişime geçiniz.")
                                window.destroy()
                        else:
                            
                            login_attempts[username_or_phone] = 1
                            messagebox.showerror("Hatalı Giriş", "Şifreyi yanlış girdiniz. 3 hakkınız kaldı.")

                                    
            else:
                
                messagebox.showerror("Hatalı Giriş", "Telefon numarasını yanlış girdiniz veya kayıtlı değilsiniz.")


        if entry_type == "Müşteri":
            
            user = guvenlik_collection.find_one({"telefon": username_or_phone})

            if user:
                
                if user.get("durum") == "Bloke edildi":
                    messagebox.showerror("Hesap Bloke Edildi", "Hesabınız bloke edilmiştir, lütfen yönetici ile iletişime geçiniz.")
                else:
                    
                    if user.get("sifre") == password:
                        L3.config(text="Giriş Başarılı...")
                        user_name = user.get("ad", "Kullanıcı")
                        welcome_message = f"Hoşgeldiniz {user_name}! Giriş başarılı, sayfaya yönlendiriliyorsunuz!"
                        messagebox.showinfo("Başarılı", welcome_message)
                        window.destroy()  
                        open_intermediate_window(username_or_phone)  
                      
                        if username_or_phone in login_attempts:
                            login_attempts[username_or_phone] = 0

                        
                        guvenlik_collection.update_one(
                            {"telefon": username_or_phone},
                            {"$inc": {"giris_sayisi": 1}}
                        )
                    else:
                        
                        if username_or_phone in login_attempts:
                            login_attempts[username_or_phone] += 1
                            remaining_attempts = 4 - login_attempts[username_or_phone]
                            if remaining_attempts > 0:
                                messagebox.showerror("Hatalı Giriş", f"Yanlış şifre girdiniz. {remaining_attempts} hakkınız kaldı.")
                            else:
                                
                                guvenlik_collection.update_one({"telefon": username_or_phone}, {"$set": {"durum": "Bloke edildi"}})
                                messagebox.showerror("Hesap Bloke Edildi", "Hesabınız 3 kez yanlış şifre girişi nedeniyle bloke edilmiştir. Lütfen yönetici ile iletişime geçiniz.")
                                window.destroy()
                        else:
                           
                            login_attempts[username_or_phone] = 1
                            messagebox.showerror("Hatalı Giriş", "Yanlış şifre girdiniz. 3 hakkınız kaldı.")
            else:
             # error mesaj
                messagebox.showerror("Hatalı Giriş", "Yanlış numara girdiniz veya kayıtlı değilsiniz.")


    # login window
    window = tk.Toplevel(root)
    window.title(f"{entry_type} Giriş Ekranı")
    window.geometry("390x220")
    window.resizable(width=False, height=False)
    window.configure(background="white")

    
    icon_path = "C:\\Users\\erkoz\\Downloads\\login.png"
    if os.path.exists(icon_path):
        window.iconbitmap(icon_path)
    else:
        messagebox.showerror("Hata", f"İkon dosyası bulunamadı: {icon_path}")

 
    image_path = "C:\\Users\\erkoz\\Downloads\\login2.png"
    if os.path.exists(image_path):
        resim = ImageTk.PhotoImage(Image.open(image_path))
        lresim = ttk.Label(window, image=resim)
        lresim.image = resim
        lresim.place(x=170, y=10)
    else:
        messagebox.showerror("Hata", f"Resim dosyası bulunamadı: {image_path}")

    
    ttk.Label(window, text="Kullanıcı Adı Veya Telefon Numarası").place(x=75, y=15)
    E1 = ttk.Entry(window, width=25)
    E1.place(x=77, y=45)

    ttk.Label(window, text="Şifre").place(x=75, y=80)
    E2 = ttk.Entry(window, show='*', width=25)
    E2.place(x=77, y=110)

  
    L3 = ttk.Label(window, text="")
    L3.place(x=148, y=200)
    L3.configure(background="white")


    bt = ttk.Button(window, text="Giriş Yap", command=giris)
    bt.place(x=75, y=150)

def add_user(name, surname, phone, password):
    
    existing_user = guvenlik_collection.find_one({"telefon": phone})
    if existing_user:
        messagebox.showerror("Hata", "Bu telefon numarası zaten kayıtlı. Lütfen başka bir numara deneyin.")
    else:
      
        guvenlik_collection.insert_one({
            "ad": name,
            "soyad": surname,
            "telefon": phone,
            "sifre": password,
            "giris_sayisi": 0,  
            "durum": "Hesap açık"
        })
        messagebox.showinfo("Başarılı", "Kullanıcı başarıyla eklendi.")


def open_t_window(action):
    t_window = tk.Toplevel(root)
    t_window.title(action)
    t_window.geometry("500x400")
    t_window.configure(background="Maroon")

    # Content of the T window
    label = ttk.Label(t_window, text=f"{action} Menüsü", font="Albertus 15 bold")
    label.pack(pady=20)
    label.configure(background="Orange")


    if action == "Kullanıcı Ekle":
        # Add user form
        ttk.Label(t_window, text="Adı:", font="Albertus 11 bold", background="Beige").pack()
        name_entry = ttk.Entry(t_window)
        name_entry.pack(pady=8)

        ttk.Label(t_window, text="Soyadı:", font="Albertus 11 bold", background="Beige").pack()
        surname_entry = ttk.Entry(t_window)
        surname_entry.pack(pady=8)

        ttk.Label(t_window, text="Telefon numarası:", font="Albertus 11 bold", background="Beige").pack()
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=8)

        ttk.Label(t_window, text="Şifre:", font="Albertus 11 bold", background="Beige").pack()
        password_entry = ttk.Entry(t_window, show='*')
        password_entry.pack(pady=8)

        tk.Button(t_window, text="Kullanıcı Ekle", background="Gray", command=lambda: [add_user(name_entry.get(), surname_entry.get(), phone_entry.get(), password_entry.get()), t_window.destroy()]).pack(pady=8)

    elif action == "Sil":
        
        ttk.Label(t_window, text="Silmek istediğiniz kişinin telefon numarasını giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=5)

        
        def delete_user():
            phone = phone_entry.get()
            if phone:
                result = guvenlik_collection.delete_one({"telefon": phone})
                if result.deleted_count > 0:
                    messagebox.showinfo("Başarılı", f"{phone} numaralı kullanıcı başarıyla silindi.")
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", f"{phone} numaralı bir kullanıcı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Telefon numarası boş olamaz.")

        tk.Button(t_window, text="Silmeyi Onayla", background="Gray", command=delete_user).pack(pady=5)

        
        ttk.Label(t_window, text="", background="Maroon").pack(pady=7)

    elif action == "Değiştir":
        
        ttk.Label(t_window, text="Telefon numarasını giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=5)

        ttk.Label(t_window, text="Yeni şifre giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        new_password_entry = ttk.Entry(t_window, show='*')
        new_password_entry.pack(pady=5)

       
        def change_password():
            phone = phone_entry.get()
            new_password = new_password_entry.get()
            if phone and new_password:
                result = guvenlik_collection.update_one({"telefon": phone}, {"$set": {"sifre": new_password}})
                if result.modified_count > 0:
                    messagebox.showinfo("Başarılı", f"{phone} numaralı kullanıcının şifresi başarıyla değiştirildi.")
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", f"{phone} numaralı bir kullanıcı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Telefon numarası veya yeni şifre boş olamaz.")

        tk.Button(t_window, text="Değişikliği Onayla", background="Gray", command=change_password).pack(pady=5)

    elif action == "Banka Hesabına Para Ekle":
       
        def add_money_to_bank_account():
            
            ttk.Label(t_window, text="Hesaba para eklemek için telefon numarasını giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
            phone_entry = ttk.Entry(t_window)
            phone_entry.pack(pady=5)

           
            ttk.Label(t_window, text="Eklenecek miktarı giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
            amount_entry = ttk.Entry(t_window)
            amount_entry.pack(pady=5)

            
            def confirm_add_money():
                phone = phone_entry.get()
                amount = float(amount_entry.get()) if amount_entry.get() else 0

                
                bank_account = banka_collection.find_one({"telefon": phone})

                if bank_account:
                    current_balance = bank_account.get("banka_bakiye", 0)
                    new_balance = current_balance + amount
                    banka_collection.update_one({"telefon": phone}, {"$set": {"banka_bakiye": new_balance}})
                    messagebox.showinfo("Başarılı", f"{phone} numaralı hesaba {amount} TL başarıyla eklendi.")
                    
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", "Belirtilen telefon numarasına ait bir hesap bulunamadı.")

            # Onay butonu
            confirm_button = tk.Button(t_window, text="Onayla", background="Gray", command=confirm_add_money)
            confirm_button.pack(pady=5)
                

        # Fonksiyonu çağırarak para ekleme penceresini açalım
        add_money_to_bank_account()


        
    elif action == "Banka Kullanıcı Sil":
        # Banka kullanıcı sil formu
        ttk.Label(t_window, text="Silmek istediğiniz banka kullanıcısının telefon numarasını giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=5)

        # Banka kullanıcı silme işlevi
        def delete_bank_user():
            phone = phone_entry.get()
            if phone:
                result = banka_collection.delete_one({"telefon": phone})
                if result.deleted_count > 0:
                    messagebox.showinfo("Başarılı", f"{phone} numaralı banka kullanıcısı başarıyla silindi.")
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", f"{phone} numaralı bir banka kullanıcısı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Telefon numarası boş olamaz.")

        tk.Button(t_window, text="Silmeyi Onayla", background="Gray", command=delete_bank_user).pack(pady=5)
        

       
        ttk.Label(t_window, text="", background="Maroon").pack(pady=5)
        
    elif action == "Bloke Koy":
        
        ttk.Label(t_window, text="Bloke etmek istediğiniz kişinin telefon numarasını giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=7)

        #  block user
        def block_user():
            phone = phone_entry.get()
            if phone:
                result = guvenlik_collection.update_one({"telefon": phone}, {"$set": {"durum": "Bloke edildi"}})
                if result.modified_count > 0:
                    messagebox.showinfo("Başarılı", f"{phone} numaralı kullanıcının hesabı başarıyla bloke edildi.")
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", f"{phone} numaralı bir kullanıcı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Telefon numarası boş olamaz.")

        tk.Button(t_window, text="Bloke Et", background="Gray", command=block_user).pack(pady=10)

        #
        ttk.Label(t_window, text="", background="Maroon").pack(pady=5)

    elif action == "Bloke Kaldır":
        # Unblock 
        ttk.Label(t_window, text="Blokesi kaldırılacak kişinin telefon numarasını giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=7)

        
        def unblock_user():
            phone = phone_entry.get()
            if phone:
                result = guvenlik_collection.update_one({"telefon": phone}, {"$set": {"durum": "Hesap açık"}})
                if result.modified_count > 0:
                    messagebox.showinfo("Başarılı", f"{phone} numaralı kullanıcının hesabının blokesi başarıyla kaldırıldı.")
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", f"{phone} numaralı bir kullanıcı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Telefon numarası boş olamaz.")

        tk.Button(t_window, text="Blokeyi Kaldır", bg="Gray", command=unblock_user).pack(pady=10)

    elif action == "Banka Bloke Koy":
      
        ttk.Label(t_window, text="Banka hesabını bloke etmek istediğiniz kişinin telefon numarasını giriniz:", font="Albertus 10 bold", background="Beige").pack(pady=5)
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=5)

        def block_user():
            phone = phone_entry.get()
            if phone:
                result = banka_collection.update_one({"telefon": phone}, {"$set": {"durum": "Bloke edildi"}})
                if result.modified_count > 0:
                    messagebox.showinfo("Başarılı", f"{phone} numaralı kullanıcının hesabı başarıyla bloke edildi.")
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", f"{phone} numaralı bir kullanıcı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Telefon numarası boş olamaz.")

        tk.Button(t_window, text="Bloke Et", background="Gray", command=block_user).pack(pady=10)

    elif action == "Banka Bloke Kaldır":
       
        ttk.Label(t_window, text="Blokesi kaldırılacak kişinin telefon numarasını giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=5)

       
        def unblock_user():
            phone = phone_entry.get()
            if phone:
                result = banka_collection.update_one({"telefon": phone}, {"$set": {"durum": "Hesap açık"}})
                if result.modified_count > 0:
                    messagebox.showinfo("Başarılı", f"{phone} numaralı kullanıcının hesabının blokesi başarıyla kaldırıldı.")
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", f"{phone} numaralı bir kullanıcı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Telefon numarası boş olamaz.")

        tk.Button(t_window, text="Blokeyi Kaldır", background="Gray", command=unblock_user).pack(pady=10)


    elif action == "Banka Değiştir":
      
        ttk.Label(t_window, text="Telefon numarasını giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        phone_entry = ttk.Entry(t_window)
        phone_entry.pack(pady=5)

        ttk.Label(t_window, text="Yeni şifre giriniz:", font="Albertus 11 bold", background="Beige").pack(pady=5)
        new_password_entry = ttk.Entry(t_window, show='*')
        new_password_entry.pack(pady=5)

    
        
        def bank_change_password():
            phone = phone_entry.get()
            new_password = new_password_entry.get()
            if phone and new_password:
                result = banka_collection.update_one({"telefon": phone}, {"$set": {"sifre": new_password}})
                if result.modified_count > 0:
                    messagebox.showinfo("Başarılı", f"{phone} numaralı kullanıcının şifresi başarıyla değiştirildi.")
                    t_window.destroy()
                else:
                    messagebox.showerror("Hata", f"{phone} numaralı bir kullanıcı bulunamadı.")
            else:
                messagebox.showerror("Hata", "Telefon numarası veya yeni şifre boş olamaz.")

        tk.Button(t_window, text="Değişikliği Onayla", background="Gray", command=bank_change_password).pack(pady=5)
        

      
        ttk.Label(t_window, text="", background="Maroon").pack(pady=5)


def open_user_list_window():
    def refresh_user_list():
        for row in tree.get_children():
            tree.delete(row)
        users = guvenlik_collection.find()
        for user in users:
            tree.insert("", "end", values=(user["ad"], user["soyad"], user.get("telefon", ""), user.get("sifre", ""), user.get("giris_sayisi", ""), user.get("durum", "Hesap açık")))
        user_list_window.after(10000, refresh_user_list)  

    user_list_window = tk.Toplevel(root)
    user_list_window.title("Kullanıcı Listesi")
    user_list_window.geometry("1600x400")
    user_list_window.configure(background="Maroon")

    tree = ttk.Treeview(user_list_window, columns=("Ad", "Soyad", "Telefon", "Şifre", "Giriş Sayısı", "Durum"), show="headings")
    tree.heading("Ad", text="Ad")
    tree.heading("Soyad", text="Soyad")
    tree.heading("Telefon", text="Telefon")
    tree.heading("Şifre", text="Şifre")
    tree.heading("Giriş Sayısı", text="Giriş Sayısı")
    tree.heading("Durum", text="Durum")

    tree.pack(expand=True, fill="both")

    refresh_user_list()  


def listele_banka_kullanicilari():
    def refresh_banka_list():
        for row in tree.get_children():
            tree.delete(row)
        users = banka_collection.find()
        for user in users:
            tree.insert("", "end", values=(
                user.get("ad"),
                user.get("soyad"),
                user.get("telefon"),
                user.get("sifre"),
                user.get("nakit_bakiye"),
                user.get("banka_bakiye"),
                user.get("giris_sayisi"),
                user.get("durum")
            ))
        list_window.after(10000, refresh_banka_list)  

    users = banka_collection.find()
    list_window = tk.Toplevel()
    list_window.title("Banka Kullanıcıları Listesi")
    list_window.configure(background="Maroon")
    list_window.geometry("1600x400")

    columns = ["Ad", "Soyad", "Telefon", "Şifre", "Nakit Bakiye", "Banka Bakiye", "Giriş Sayısı", "Hesap Durumu"]
    tree = ttk.Treeview(list_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)

    for user in users:
        tree.insert("", "end", values=(
            user.get("ad"),
            user.get("soyad"),
            user.get("telefon"),
            user.get("sifre"),
            user.get("nakit_bakiye"),
            user.get("banka_bakiye"),
            user.get("giris_sayisi"),
            user.get("durum")
        ))

    tree.pack(fill=tk.BOTH, expand=True)

    refresh_banka_list()  
    


def add_bank_account():
    # Yeni bir pencere aç
    add_bank_window = tk.Toplevel(root)
    add_bank_window.title("Banka Hesap Ekle")
    add_bank_window.geometry("400x300")
    add_bank_window.configure(background="Maroon")

    # Label ve entryler için yerleşim ayarları
    ttk.Label(add_bank_window, text="Banka Hesap Ekle Menüsü", background="Orange", font="Albertus 15 bold").grid(padx=80, pady=10, columnspan=2)

    ttk.Label(add_bank_window, text="Adı:", font="Albertus 10 bold", background="Beige").grid(row=1, column=0, padx=10, pady=5, sticky="E")
    ad_entry = ttk.Entry(add_bank_window)
    ad_entry.grid(row=1, column=1, padx=10, pady=5, sticky="W")

    ttk.Label(add_bank_window, text="Soyadı:", font="Albertus 10 bold", background="Beige").grid(row=2, column=0, padx=10, pady=5, sticky="E")
    soyad_entry = ttk.Entry(add_bank_window)
    soyad_entry.grid(row=2, column=1, padx=10, pady=5, sticky="W")

    ttk.Label(add_bank_window, text="Telefon:", font="Albertus 10 bold", background="Beige").grid(row=3, column=0, padx=10, pady=5, sticky="E")
    telefon_entry = ttk.Entry(add_bank_window)
    telefon_entry.grid(row=3, column=1, padx=10, pady=5, sticky="W")

    ttk.Label(add_bank_window, text="Şifre:", font="Albertus 10 bold", background="Beige").grid(row=4, column=0, padx=10, pady=5, sticky="E")
    sifre_entry = ttk.Entry(add_bank_window, show='*')
    sifre_entry.grid(row=4, column=1, padx=10, pady=5, sticky="W")

    # Kaydet butonu işlevi
    def kaydet():
        ad = ad_entry.get()
        soyad = soyad_entry.get()
        telefon = telefon_entry.get()
        sifre = sifre_entry.get()

        # Boş giriş var mı kontrol et
        if not ad or not soyad or not telefon or not sifre:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurunuz.")
            return

        # Girilen telefon numarasına ait banka kullanıcısını kontrol et
        bank_user = banka_collection.find_one({"telefon": telefon})
        if bank_user:  # Banka kullanıcısı bulunduysa
            messagebox.showerror("Hata", "Girdiğiniz telefon numarasına ait bir banka kullanıcısı zaten var.")
        else:  # Banka kullanıcısı bulunamadıysa
            # Banka kullanıcısını ekleyin
            banka_data = {
                "ad": ad,
                "soyad": soyad,
                "telefon": telefon,
                "sifre": sifre,
                "nakit_bakiye": 0,
                "banka_bakiye": 5000,  # Otomatik olarak 5000 TL eklenir
                "durum": "Hesap açık"  # Hesap durumu eklenir
            }
            banka_collection.insert_one(banka_data)
            messagebox.showinfo("Başarılı", "Banka hesabı başarıyla eklendi.")
            add_bank_window.destroy()

    tk.Button(add_bank_window, text="Kaydet", background="Gray", font="Albertus 10 bold", command=kaydet).grid(row=5, column=0, columnspan=2, padx=20, pady=25)




# second window
def open_second_window(entry_type, bank_account_data, username_or_phone):
    second_window = tk.Toplevel(root)
    second_window.title(f"{entry_type} Menü")
    second_window.geometry("400x930")
    second_window.configure(background="Maroon")

    def canli_destek_konusmalari():
        # Yeni pencere oluştur
        konusmalar_penceresi = Toplevel(second_window)
        konusmalar_penceresi.title("Canlı Destek Konuşmaları")
        konusmalar_penceresi.geometry("600x500")

        def guncelle_konusmalar():
            # Metin alanını düzenleme moduna geçir
            konusmalar_text.config(state="normal")
            # Metin alanını temizle
            konusmalar_text.delete("1.0", "end")

            # Tüm kaydedilen konuşmaları çek
            konusmalar = destek_collection.find({"status": "closed"})
            for konusma in konusmalar:
                # Her bir konuşmayı metin alanına ekle
                konusmalar_text.insert("end", f"{konusma['user']} : {konusma['message']}\n")

            # Metin alanını düzenleme modundan çıkar
            konusmalar_text.config(state="disabled")

            # 10 saniyede bir güncelle
            konusmalar_penceresi.after(10000, guncelle_konusmalar)

        # Metin alanı oluştur ve konuşmaları eklemek için kullan
        konusmalar_text = Text(konusmalar_penceresi, background="Orange", state="disabled")
        konusmalar_text.pack(expand=True, fill="both")

        # İlk konuşmaları almak için fonksiyonu çağır
        guncelle_konusmalar()
    
    # Yönetici Destek Functions
    def yonetici_destek():
        destek_penceresi = Toplevel(second_window)
        destek_penceresi.title("Destek Mesajları")
        destek_penceresi.geometry("600x500")

        def guncelle_mesajlar():
            messages_text.config(state="normal")
            messages_text.delete("1.0", "end")  # Tüm metni temizle

            messages = destek_collection.find({"status": "active"})
            for message in messages:
                messages_text.insert("end", f"{message['user']} : {message['message']}\n")

            messages_text.config(state="disabled")  # Metin alanını tekrar düzenlenebilir olmaktan çıkar

            destek_penceresi.after(10000, guncelle_mesajlar)  # 10 saniyede bir güncelle

        def cevap_gonder(message, cevap):
            destek_collection.insert_one({"user": "Yönetici", "message": cevap, "status": "active"})
            messagebox.showinfo("Bilgi", "Cevap Gönderildi!")
            guncelle_mesajlar()

        def sohbeti_sonlandir():
            destek_collection.update_many({"status": "active"}, {"$set": {"status": "closed"}})
            messagebox.showinfo("Bilgi", "Sohbet Sonlandırıldı ve Kaydedildi!")
            destek_penceresi.destroy()

        messages_text = Text(destek_penceresi, background="Orange", state="disabled")
        messages_text.pack(expand=True, fill="both")

        entry_frame = Frame(destek_penceresi, background="Navy Blue")
        entry_frame.pack(fill="x")

        cevap_entry = Entry(entry_frame, width=50)
        cevap_entry.pack(side="left", padx=5)

        Button(entry_frame, text="Cevapla", background="Gray", command=lambda: cevap_gonder(messages_text.get("1.0", "end-1c"), cevap_entry.get())).pack(side="left", padx=5)
        Button(entry_frame, text="Sohbeti Sonlandır", background="Gray", command=sohbeti_sonlandir).pack(side="right", padx=5)

        # İlk mesajları almak için
        guncelle_mesajlar()

    def open_e_window(action):
        e_window = tk.Toplevel(second_window)
        e_window.title(action)
        e_window.geometry("500x350")
        e_window.configure(background="Maroon")

        label = ttk.Label(e_window, text=f"{action} Menüsü ", background="Orange", font="Verdana 12 bold")
        label.pack(pady=20)

        if action == "Para Çekme":
            ttk.Label(e_window, text="Çekilecek miktarı giriniz:", font="Futura 10 bold", background="Beige").pack(pady=10)
            miktar_entry = ttk.Entry(e_window)
            miktar_entry.pack(pady=20)

            def para_cekme_with_amount():
                try:
                    miktar = float(miktar_entry.get())
                    bank_account_data = banka_collection.find_one({"telefon": username_or_phone})

                    if bank_account_data:
                        banka_bakiye = bank_account_data.get('banka_bakiye', 0)
                        if banka_bakiye >= miktar:
                            banka_bakiye -= miktar
                            nakit_bakiye = bank_account_data.get('nakit_bakiye', 0)
                            nakit_bakiye += miktar

                            banka_collection.update_one({"telefon": username_or_phone}, {"$set": {"banka_bakiye": banka_bakiye}})
                            banka_collection.update_one({"telefon": username_or_phone}, {"$set": {"nakit_bakiye": nakit_bakiye}})

                            messagebox.showinfo("Başarılı", "Bankadaki paranız başarıyla çekildi ve nakite dönüştürüldü!")
                            e_window.destroy()
                        else:
                            messagebox.showerror("Hata", "Yetersiz bakiye.")
                    else:
                        messagebox.showerror("Hata", "Banka hesabı bulunamadı.")
                except ValueError:
                    messagebox.showerror("Hata", "Geçerli bir miktar giriniz.")

            tk.Button(e_window, text="Onayla", bg="Gray", font="Futura 10 bold", command=para_cekme_with_amount).pack(pady=10)

        elif action == "Para Yatırma":
            ttk.Label(e_window, text="Yatırılacak miktarı giriniz:", font="Futura 10 bold", background="Beige").pack(pady=10)
            miktar_entry = ttk.Entry(e_window)
            miktar_entry.pack(pady=20)

            def para_yatirma_with_amount():
                try:
                    miktar = float(miktar_entry.get())
                    bank_account_data = banka_collection.find_one({"telefon": username_or_phone})

                    if bank_account_data:
                        nakit_bakiye = bank_account_data.get('nakit_bakiye', 0)
                        if nakit_bakiye >= miktar:
                            nakit_bakiye -= miktar
                            banka_bakiye = bank_account_data.get('banka_bakiye', 0)
                            banka_bakiye += miktar

                            banka_collection.update_one({"telefon": username_or_phone}, {"$set": {"banka_bakiye": banka_bakiye}})
                            banka_collection.update_one({"telefon": username_or_phone}, {"$set": {"nakit_bakiye": nakit_bakiye}})

                            messagebox.showinfo("Başarılı", "Nakit paranız başarıyla bankanıza yatırıldı!")
                            e_window.destroy()
                        else:
                            messagebox.showerror("Hata", "Yetersiz bakiye.")
                    else:
                        messagebox.showerror("Hata", "Banka hesabı bulunamadı.")
                except ValueError:
                    messagebox.showerror("Hata", "Geçerli bir miktar giriniz.")

            tk.Button(e_window, text="Onayla", bg="Gray", font="Futura 10 bold", command=para_yatirma_with_amount).pack(pady=10)

        elif action == "Para Transferi":
            ttk.Label(e_window, text="Transfer edilecek hesabın telefon numarasını giriniz:", font="Futura 10 bold", background="Beige").pack(pady=10)
            telefon_entry = ttk.Entry(e_window)
            telefon_entry.pack(pady=20)

            ttk.Label(e_window, text="Transfer edilecek miktarı giriniz:", font="Futura 10 bold", background="Beige").pack(pady=10)
            miktar_entry = ttk.Entry(e_window)
            miktar_entry.pack(pady=20)

            def para_transfer_with_amount():
                try:
                    miktar = float(miktar_entry.get())
                    transfer_to = telefon_entry.get()
                    sender_data = banka_collection.find_one({"telefon": username_or_phone})
                    receiver_data = banka_collection.find_one({"telefon": transfer_to})

                    if sender_data and receiver_data:
                        sender_banka_bakiye = sender_data.get('banka_bakiye', 0)
                        if sender_banka_bakiye >= miktar:
                            sender_banka_bakiye -= miktar
                            receiver_banka_bakiye = receiver_data.get('banka_bakiye', 0)
                            receiver_banka_bakiye += miktar

                            banka_collection.update_one({"telefon": username_or_phone}, {"$set": {"banka_bakiye": sender_banka_bakiye}})
                            banka_collection.update_one({"telefon": transfer_to}, {"$set": {"banka_bakiye": receiver_banka_bakiye}})

                            messagebox.showinfo("Başarılı", "Para başarıyla transfer edildi!")
                            e_window.destroy()
                        else:
                            messagebox.showerror("Hata", "Yetersiz bakiye.")
                    else:
                        messagebox.showerror("Hata", "Transfer edilecek hesap bulunamadı.")
                except ValueError:
                    messagebox.showerror("Hata", "Geçerli bir miktar giriniz.")

            tk.Button(e_window, text="Onayla", bg="Gray", font="Futura 10 bold", command=para_transfer_with_amount).pack(pady=10)



    def refresh_window():
        second_window.destroy()
        bank_account_data = banka_collection.find_one({"telefon": username_or_phone})
        open_second_window(entry_type, bank_account_data, username_or_phone)



    if entry_type == "Yönetici":
       
        L1 = tk.Label(second_window, text="Bir İşlem Seçiniz", font="Verdana 12 bold", bg="Orange")
        L1.pack(pady=10)

       
        btn0 = tk.Button(second_window, text="Kullanıcıları Listele", command=open_user_list_window, bg='gray', font="Arial 10")
        btn0.pack(pady=10)

        btn3 = tk.Button(second_window, text="Kullanıcı Ekle", command=lambda: open_t_window("Kullanıcı Ekle"), bg='gray', font="Arial 10")
        btn3.pack(pady=10)


        btn1 = tk.Button(second_window, text="Değiştir", command=lambda: open_t_window("Değiştir"), bg='gray', font="Arial 10")
        btn1.pack(pady=10)

        btn2 = tk.Button(second_window, text="Kullanıcı Listesinden Sil", command=lambda: open_t_window("Sil"), bg='gray', font="Arial 10")
        btn2.pack(pady=10)

        btn4 = tk.Button(second_window, text="Bloke Kaldır", command=lambda: open_t_window("Bloke Kaldır"), bg='gray', font="Arial 10")
        btn4.pack(pady=10)

        btn5 = tk.Button(second_window, text="Bloke Koy", command=lambda: open_t_window("Bloke Koy"), bg='gray', font="Arial 10")
        btn5.pack(pady=10)

        btnara= tk.Label(second_window, text="--------------------------------------------", background="Maroon", font="Georgia 15 bold")
        btnara.pack(pady=10)

        btn01 = tk.Button(second_window, text="Banka Kullanıcıları Listele", command=listele_banka_kullanicilari, bg='gray', font="Arial 10")
        btn01.pack(pady=10)

        btn6 = tk.Button(second_window, text="Banka Hesap Ekle", command=add_bank_account, bg='gray', font="Arial 10")
        btn6.pack(pady=10)

        btn7 = tk.Button(second_window, text="Banka Kullanıcı Listesinden Sil", command=lambda: open_t_window("Banka Kullanıcı Sil"), bg='gray', font="Arial 10")
        btn7.pack(pady=10)

        btn07 = tk.Button(second_window, text="Banka Kullanıcı Değiştir", command=lambda: open_t_window("Banka Değiştir"), bg='gray', font="Arial 10")
        btn07.pack(pady=10)

        btn08 = tk.Button(second_window, text="Banka Hesap Bloke Koy", command=lambda: open_t_window("Banka Bloke Koy"), bg='gray', font="Arial 10")
        btn08.pack(pady=10)

        btn008 = tk.Button(second_window, text="Banka Hesap Bloke Kaldır", command=lambda: open_t_window("Banka Bloke Kaldır"), bg='gray', font="Arial 10")
        btn008.pack(pady=10)

        btn9 = tk.Button(second_window, text="Banka Hesabına Para Ekle", command=lambda: open_t_window("Banka Hesabına Para Ekle"), bg='gray', font="Arial 10")
        btn9.pack(pady=10)

        btnaraa= tk.Label(second_window, text="--------------------------------------------", background="Maroon", font="Georgia 15 bold")
        btnaraa.pack(pady=10)

        yonetici_destek_butonu = Button(second_window, text="Destek Mesajları", background="Orange", font="Arial 10", command=yonetici_destek)
        yonetici_destek_butonu.pack(pady=10)

        btn10 = tk.Button(second_window, text="Canlı Destek Konuşmaları", command=canli_destek_konusmalari, bg='Orange', font="Arial 10")
        btn10.pack(pady=10)

        btn8 = tk.Button(second_window, text="Çıkış", command=second_window.destroy, bg='gray', font="Arial 10")
        btn8.pack(pady=10)

        


    elif entry_type == "Banka":
        A1 = ttk.Label(second_window, background="Orange", text="Bir İşlem Seçiniz", font="Verdana 15 bold")
        A1.pack(pady=20)

       
        nakit_label = tk.Label(second_window, background="Beige", font="Futura 12 bold", text=f"Nakit Bakiye: {bank_account_data.get('nakit_bakiye', 0)} TL")
        nakit_label.pack(pady=15)

        banka_label = ttk.Label(second_window, background="Beige", font="Futura 12 bold", text=f"Banka Bakiye: {bank_account_data.get('banka_bakiye', 0)} TL")
        banka_label.pack(pady=15)

        toplam_label = ttk.Label(second_window, background="Beige", font="Futura 12 bold", text=f"Toplam Bakiye: {bank_account_data.get('nakit_bakiye', 0) + bank_account_data.get('banka_bakiye', 0)} TL")
        toplam_label.pack(pady=15)

       
        
        btn_para_cekme = tk.Button(second_window, text="Para Çekme", command=lambda: open_e_window("Para Çekme"), bg="Beige", font="Futura 10 bold")
        btn_para_cekme.pack(pady=15)

        btn_para_yatirma = tk.Button(second_window, text="Para Yatırma", command=lambda: open_e_window("Para Yatırma"), bg="Beige", font="Futura 10 bold")
        btn_para_yatirma.pack(pady=15)

        btn_para_transferi = tk.Button(second_window, text="Para Transferi", command=lambda: open_e_window("Para Transferi"), bg="Beige", font="Futura 10 bold")
        btn_para_transferi.pack(pady=15)

        btn_yenile = tk.Button(second_window, text="Sayfayı Yenile", command=refresh_window, bg="Beige", font="Futura 8 bold")
        btn_yenile.pack(pady=80)



# Main function to open the intermediate window
def open_intermediate_window(username_or_phone):
    intermediate_window = tk.Toplevel(root)
    intermediate_window.title("Kapı Açıldı")
    intermediate_window.geometry("700x450")

    # Countdown 
    countdown_label = ttk.Label(intermediate_window, text="Kapı Açıldı! 10 dakika süreniz var istediğiniz zaman çıkabilirsiniz.")
    countdown_label.pack(pady=20)

    # Update the countdown
    def update_countdown(total_seconds):
        minutes, seconds = divmod(total_seconds, 60)
        countdown_label.config(text=f"Kapı Açıldı! {minutes:02}:{seconds:02} kaldı.")
        if total_seconds > 0:
            intermediate_window.after(1000, update_countdown, total_seconds - 1)
        else:
            intermediate_window.destroy()
            open_rating_window()

    # 10 dakikalık countdown (600 saniye)
    update_countdown(600)
    play_background_music()  # Arka plan müziğini çal

    def change_password():
        change_window = tk.Toplevel(intermediate_window)
        change_window.title("Kullanıcı Şifreni Değiştir")
        change_window.geometry("300x350")

        ttk.Label(change_window, text="Eski Şifre").pack(pady=5)
        old_password_entry = ttk.Entry(change_window, show='*')
        old_password_entry.pack(pady=5)

        ttk.Label(change_window, text="Yeni Şifre").pack(pady=5)
        new_password_entry = ttk.Entry(change_window, show='*')
        new_password_entry.pack(pady=5)

        ttk.Label(change_window, text="Yeni Şifre (Tekrar)").pack(pady=5)
        confirm_password_entry = ttk.Entry(change_window, show='*')
        confirm_password_entry.pack(pady=5)

        def confirm_change():
            old_password = old_password_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            user = guvenlik_collection.find_one({"telefon": username_or_phone})
            if user and user.get("sifre") == old_password:
                if new_password != old_password:  # Yeni şifre eski şifreyle aynı değilse devam et
                    if new_password == confirm_password:
                        guvenlik_collection.update_one({"telefon": username_or_phone}, {"$set": {"sifre": new_password}})
                        messagebox.showinfo("Başarılı", "Şifre başarıyla değiştirildi!")
                        change_window.destroy()
                    else:
                        messagebox.showerror("Hata", "Yeni şifreler uyuşmuyor!")
                else:
                    messagebox.showerror("Hata", "Yeni şifre eski şifre ile aynı olamaz!")
            else:
                messagebox.showerror("Hata", "Eski şifre yanlış!")

        ttk.Button(change_window, text="Onayla", command=confirm_change).pack(pady=10)

    change_password_button = ttk.Button(intermediate_window, text="Kullanıcı Şifreni Değiştir", command=change_password)
    change_password_button.pack(pady=10)

    # Add the image between the buttons
    qr_image = Image.open("C:/Users/erkoz/Downloads/qr.png")
    qr_image = qr_image.resize((200, 200), Image.Resampling.LANCZOS)
    qr_photo = ImageTk.PhotoImage(qr_image)

    qr_label = ttk.Label(intermediate_window, image=qr_photo)
    qr_label.image = qr_photo  # Keep a reference to avoid garbage collection
    qr_label.pack(pady=20)

    # Exit 
    def exit_window():
        intermediate_window.destroy()
        open_rating_window()  # ana menü dönme

    exit_button = ttk.Button(intermediate_window, text="Çıkış", command=exit_window)
    exit_button.pack(side=tk.BOTTOM, pady=10)


# değerlendirme
def open_rating_window():
    global rating_window  
    rating_window = tk.Toplevel(root)
    rating_window.title("Müşteri Menü")
    rating_window.geometry("300x400")

    
    L1 = ttk.Label(rating_window, text="BİZİ DEĞERLENDİRİNİZ", font="College 12 bold")
    L1.pack(pady=10)

    
    btn1 = ttk.Button(rating_window, text="★ ★ ★ ★ ★ ", command=lambda: open_comment_window(5))
    btn1.pack(pady=12)

    btn2 = ttk.Button(rating_window, text="★ ★ ★ ★ ", command=lambda: open_comment_window(4))
    btn2.pack(pady=12)

    btn3 = ttk.Button(rating_window, text="★ ★ ★  ", command=lambda: open_comment_window(3))
    btn3.pack(pady=12)

    btn4 = ttk.Button(rating_window, text="★ ★  ", command=lambda: open_comment_window(2))
    btn4.pack(pady=12)

    btn5 = ttk.Button(rating_window, text="★", command=lambda: open_comment_window(1))
    btn5.pack(pady=12)


# yorum penceresi
def open_comment_window(rating):
    comment_window = tk.Toplevel(root)
    comment_window.title("Yorum Yazınız")

   
    L1 = ttk.Label(comment_window, text="Yorumunuzu Yazınız:", font="Verdana 12 bold")
    L1.pack(pady=10)

    
    comment_textbox = tk.Text(comment_window, width=40, height=10)
    comment_textbox.pack(pady=10)

  
    def submit_comment():
        comment = comment_textbox.get("1.0", tk.END).strip()
        if comment:
            if rating == 5:
                messagebox.showinfo("Teşekkürler", f"Teşekkür ederiz! Değerlendirmeniz için çok memnun olduk.\nYorumunuz: {comment}")
            elif rating == 4:
                messagebox.showinfo("Teşekkürler", f"Teşekkür ederiz! Daha iyisini yapabilmek için elimizden geleni yapacağız.\nYorumunuz: {comment}")
            elif rating == 3:
                messagebox.showinfo("Teşekkürler", f"Anlayışınız için teşekkür ederiz. Sizden gelen geribildirim bizim için önemlidir.\nYorumunuz: {comment}")
            elif rating == 2:
                messagebox.showinfo("Teşekkürler", f"Özür dileriz! Daha iyi hizmet vermek için çalışacağız.\nYorumunuz: {comment}")
            elif rating == 1:
                messagebox.showinfo("Teşekkürler", f"Özür dileriz! Deneyimlerinizle ilgili daha fazla bilgi almak isteriz. Lütfen bizimle iletişime geçin.\nYorumunuz: {comment}")
            else:
                messagebox.showwarning("Uyarı", "Yorum alanı boş olamaz.")
            comment_window.destroy()
            rating_window.destroy()  
            stop_background_music()  # Arka plan müziğini durdur
            root.deiconify()  

    
    submit_btn = ttk.Button(comment_window, text="Gönder", command=submit_comment)
    submit_btn.pack(pady=10)



def ac_canli_destek():
    canli_destek_penceresi = Toplevel(root)
    canli_destek_penceresi.title("Canlı Destek")
    canli_destek_penceresi.geometry("500x500")
    canli_destek_penceresi.configure(background="Navy Blue")

    def guncelle_mesajlar():
        messages_text.config(state="normal", background="Orange")
        messages_text.delete("1.0", "end")  # Tüm metni temizle

        messages = destek_collection.find({"status": "active"})
        for message in messages:
            messages_text.insert("end", f"{message['user']} : {message['message']}\n")

        messages_text.config(state="disabled")  # Metin alanını tekrar düzenlenebilir olmaktan çıkar

        canli_destek_penceresi.after(10000, guncelle_mesajlar)  # 10 saniyede bir güncelle

    def sorun_gonder():
        sorun = sorun_entry.get()
        destek_collection.insert_one({"user": "Üye", "message": sorun, "status": "active"})
        sorun_entry.delete(0, 'end')
        guncelle_mesajlar()

    Label(canli_destek_penceresi, text="!!!!! DİKKAT !!!!!\nGörüşmeleriniz kalite standartları gereği kayıt altına alınmaktadır.", background="Orange", font="Arial 10").pack(pady=5)
    Label(canli_destek_penceresi, text="Sorununuzu Giriniz:", background="Green", font="Arial 10").pack(pady=5)
    sorun_entry = Entry(canli_destek_penceresi, width=50)
    sorun_entry.pack(pady=5)

    Button(canli_destek_penceresi, text="Gönder", background="Gray", font="Arial 10", command=sorun_gonder).pack(pady=5)
    Button(canli_destek_penceresi, text="Sohbeti Sonlandır", background="Gray", font="Arial 10", command=lambda: sohbeti_sonlandir(canli_destek_penceresi)).pack(pady=5)

    messages_text = Text(canli_destek_penceresi, state="disabled")
    messages_text.pack(expand=True, fill="both")

    # İlk mesajları almak için
    guncelle_mesajlar()

def sohbeti_sonlandir(pencere):
    destek_collection.update_many({"status": "active"}, {"$set": {"status": "closed"}})
    messagebox.showinfo("Bilgi", "Sohbet Sonlandırıldı ve Kaydedildi!")
    pencere.destroy()




def buton():
    lbl.config(text="Yönetici girişi seçildi")
    show_message("Yönetici", "Yönetici girişi seçildi")
    open_login_window("Yönetici")


def buton2():
    lbl.config(text="Müşteri girişi seçildi")
    show_message("Müşteri", "Müşteri girişi seçildi")
    open_login_window("Müşteri")


def buton3():
    lbl.config(text="Banka girişi seçildi")
    show_message("Banka", "Banka girişi seçildi")
    open_login_window("Banka")


def add_bank_data(name, surname, password, phone):
    bank_data = {
        "ad": name,
        "soyad": surname,
        "telefon": phone,
        "sifre": password,
        "nakit_bakiye": 0,
        "banka_bakiye": 5000,  # Otomatik olarak 5000 TL eklenir
        "durum": "Hesap açık"  # Hesap durumu eklenir
    }
    banka_collection.insert_one(bank_data)

def add_user_and_bank_data(name, surname, phone, password):
    add_user(name, surname, phone, password)  # Kullanıcı verisini ekle
    add_bank_data(name, surname, password, phone)  # Banka verisini ekle
    messagebox.showinfo("Başarılı", "Kullanıcı ve banka verisi başarıyla eklendi.")



root = tk.Tk()
root.title("Ana Ekran # EFELER")
root.geometry("500x400")
root.configure(background="Maroon") 


L0 = ttk.Label(root, text="HOŞGELDİNİZ", font="Georgia 15 bold")
L0.pack(pady=10)
L0.configure(background="Beige")

L1 = ttk.Label(root, text="LÜTFEN BİR GİRİŞ SEÇİNİZ", font="Georgia 15 bold")
L1.pack(pady=10)    
L1.configure(background="Beige")




btn = tk.Button(root, text="Yönetici", font="Albertus 12 bold", background="Gray", command=buton)
btn.pack(pady=20)


btn2 = tk.Button(root, text="Müşteri", font="Albertus 12 bold", background="Gray", command=buton2)
btn2.pack(pady=20)


btn3 = tk.Button(root, text="Banka", font="Albertus 12 bold", background="Gray", command=buton3)
btn3.pack(pady=20)

canli_destek_butonu = Button(root, text="Canlı Destek", background="Orange", command=ac_canli_destek)
canli_destek_butonu.pack(pady=10)


lbl = ttk.Label(root, text="", font="Albertus 10 bold")
lbl.pack(pady=10)
lbl.configure(background="maroon")

root.mainloop()
               

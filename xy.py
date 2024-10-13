import os
import random
from tkinter import Tk, Label, Button, Canvas, filedialog, messagebox
from PIL import Image, ImageTk
import time

class ImageSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Chọn tọa độ x, y của ảnh")

        self.text_label = Label(self.root, text="Nội dung của file txt sẽ hiển thị ở đây", font=("Arial", 24))
        self.text_label.pack(pady=5)

        self.select_folder_button = Button(self.root, text="Chọn thư mục ảnh", command=self.select_folder)
        self.select_folder_button.pack(pady=5)

        self.canvas = Canvas(self.root, width=400, height=400)
        self.canvas.pack(pady=5)

        self.coordinates_label = Label(self.root, text="Chưa chọn tọa độ", font=("Arial", 12))
        self.coordinates_label.pack(pady=5)

        self.percentage_label = Label(self.root, text="Phần trăm số dòng: 0%", font=("Arial", 12))
        self.percentage_label.pack(pady=5)

        self.estimated_time_label = Label(self.root, text="Thời gian ước tính hoàn thành: 0 giây", font=("Arial", 12))
        self.estimated_time_label.pack(pady=5)

        self.image_list = []
        self.image_path = None
        self.img = None
        self.line = None
        self.history = []  
        self.start_time = None  
        self.processed_images = 0  

        self.canvas.bind("<Motion>", self.update_line_position)
        self.canvas.bind("<Button-1>", self.get_coordinates)

        self.root.bind('<Button-3>', self.delete_image_and_txt)

        self.root.bind('<Control-z>', self.undo_image)

    def select_folder(self):

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.image_list = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected) if f.endswith('.jpeg')]
            if self.image_list:
                self.load_random_image()

                self.select_folder_button.pack_forget()

                self.update_percentage()

            else:
                self.coordinates_label.config(text="Không tìm thấy ảnh trong thư mục.")

    def load_random_image(self):

        random_image = random.choice(self.image_list)

        while self.is_image_in_file(random_image):
            random_image = random.choice(self.image_list)

        self.image_path = random_image
        img = Image.open(self.image_path)
        img.thumbnail((400, 400))  
        self.img = ImageTk.PhotoImage(img)

        self.canvas.delete("all")  

        self.canvas.create_image(0, 0, anchor="nw", image=self.img)

        self.display_text_for_image(self.image_path)

        if self.line:
            self.canvas.delete(self.line)

    def is_image_in_file(self, image_path):

        if os.path.exists("coordinates.txt"):
            with open("coordinates.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    if image_path in line:
                        return True
        return False

    def update_line_position(self, event):

        if self.line:
            self.canvas.delete(self.line)
        self.line = self.canvas.create_line(0, event.y, 400, event.y, fill="red")

    def get_coordinates(self, event):

        x, y = event.x, event.y
        self.coordinates_label.config(text=f"Tọa độ bạn chọn: x={x}, y={y}")

        self.save_coordinates(x, y)

        self.load_random_image()

        self.update_percentage()

    def save_coordinates(self, x, y):

        with open("coordinates.txt", "a", encoding="utf-8") as file:
            file.write(f"File: {self.image_path}, x: {x}, y: {y}\n")
            self.processed_images += 1  

    def display_text_for_image(self, image_path):

        txt_file = image_path.replace('.jpeg', '.txt')

        if os.path.exists(txt_file):
            with open(txt_file, "r", encoding="utf-8") as file:
                content = file.read()
                self.text_label.config(text=content)
        else:
            self.text_label.config(text="Không tìm thấy file txt tương ứng.")

    def update_percentage(self):

        total_files = len(self.image_list)

        if os.path.exists("coordinates.txt"):
            with open("coordinates.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()
                line_count = len(lines)
        else:
            line_count = 0

        percentage = 0
        if total_files > 0:
            percentage = (line_count / (total_files)) * 100

        self.percentage_label.config(text=f"Phần trăm số dòng: {percentage:.2f}%")

        estimated_time = self.calculate_estimated_time()
        self.estimated_time_label.config(text=f"Thời gian ước tính hoàn thành: {estimated_time} giây")

    def calculate_estimated_time(self):

        if self.processed_images > 0 and self.start_time is not None:
            elapsed_time = time.time() - self.start_time  
            estimated_total_time = (elapsed_time / self.processed_images) * len(self.image_list)
            remaining_time = estimated_total_time - elapsed_time
            return int(remaining_time)  
        return 0

    def delete_image_and_txt(self, event):
        if self.image_path:

            confirm = True
            if confirm:

                if os.path.exists(self.image_path):
                    os.remove(self.image_path)

                txt_file = self.image_path.replace('.jpeg', '.txt')
                if os.path.exists(txt_file):
                    os.remove(txt_file)

                self.load_random_image()

                self.update_percentage()
        else:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh nào được chọn để xóa.")

    def undo_image(self, event):

        if self.history:
            self.image_path = self.history.pop()
            img = Image.open(self.image_path)
            img.thumbnail((400, 400))  
            self.img = ImageTk.PhotoImage(img)

            self.canvas.delete("all")  
            self.canvas.create_image(0, 0, anchor="nw", image=self.img)

            self.display_text_for_image(self.image_path)
            self.update_percentage()

app_start_time = time.time()

root = Tk()
app = ImageSelector(root)
app.start_time = app_start_time  
root.mainloop()
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Đường dẫn đến folder chứa ảnh và file txt
dataset_path = input()
confirmed_images_file = "confirmed_unselect.txt"  # File lưu ảnh không được chọn

# Load các ảnh từ confirmed.txt
def load_confirmed_images():
    if not os.path.exists(confirmed_images_file):
        return set()
    with open(confirmed_images_file, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file)

# Lưu các ảnh không được chọn vào file txt (dồn dòng)
def save_confirmed_images(confirmed_images):
    # Đọc các ảnh hiện có trong confirmed.txt
    existing_images = load_confirmed_images()

    # Kết hợp với các ảnh mới không được chọn
    all_images = existing_images.union(set(confirmed_images))

    # Ghi lại vào file confirmed.txt
    with open(confirmed_images_file, "w", encoding="utf-8") as file:
        file.writelines(f"{img}\n" for img in all_images)

# Load ảnh và label từ folder dataset
def load_images_and_labels():
    confirmed_images = load_confirmed_images()
    images_and_labels = []

    def add_image(img_name, image_path, label_path):
        if os.path.exists(label_path):
            with open(label_path, "r", encoding="utf-8") as label_file:
                label = label_file.read().strip()
            images_and_labels.append((image_path, label))

    # Load từ dataset folder
    for filename in os.listdir(dataset_path):
        if filename.endswith(".jpeg"):
            img_name = filename[:-5]  # Bỏ phần đuôi ".jpeg"
            image_path = os.path.join(dataset_path, filename)
            label_path = os.path.join(dataset_path, f"{img_name}.txt")
            
            # Kiểm tra xem ảnh đã có trong confirmed_images chưa
            if image_path not in confirmed_images:
                add_image(img_name, image_path, label_path)

            if len(images_and_labels) >= 40:  # Chỉ load tối đa 40 ảnh
                break

    return images_and_labels

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.selected_images = []  # Mảng lưu các ảnh đã chọn
        self.images_and_labels = load_images_and_labels()  # Load ảnh ban đầu

        self.create_widgets()

    # Tạo giao diện để hiển thị ảnh và label
    def create_widgets(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.display_images()  # Hiển thị ảnh ban đầu

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side=tk.BOTTOM)

        delete_btn = tk.Button(btn_frame, text="Chuyển Tabs (Xóa ảnh)", command=self.switch_to_next_tab)
        delete_btn.pack(side=tk.LEFT)

    # Hiển thị ảnh và label
    def display_images(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        for i, (image_path, label) in enumerate(self.images_and_labels):
            frame = tk.Frame(self.main_frame, relief=tk.RAISED, bd=2)
            frame.grid(row=i // 10, column=i % 10, padx=10, pady=10)

            # Load ảnh
            img = Image.open(image_path)
            img.thumbnail((100, 100))  # Resize ảnh
            img = ImageTk.PhotoImage(img)

            img_label = tk.Label(frame, image=img)
            img_label.image = img
            img_label.pack()

            label_text = tk.Label(frame, text=label, font=("Helvetica", 15))
            label_text.pack()

            check_var = tk.IntVar()
            checkbox = tk.Checkbutton(frame, text="Chọn", variable=check_var)
            checkbox.pack()
            self.selected_images.append((image_path, check_var))  # Thêm ảnh và checkbox vào mảng

    # Xóa ảnh đã chọn và lưu ảnh không được chọn vào confirmed.txt
    def switch_to_next_tab(self):
        to_delete = [img for img, var in self.selected_images if var.get() == 1]  # Ảnh được chọn để xóa
        to_keep = [img for img, var in self.selected_images if var.get() == 0]  # Ảnh không được chọn để lưu

        # Xóa ảnh đã chọn
        for img_path in to_delete:
            label_path = img_path.replace(".jpeg", ".txt")
            try:
                os.remove(img_path)  # Xóa ảnh
                os.remove(label_path)  # Xóa file txt tương ứng
            except OSError as e:
                messagebox.showerror("Lỗi", f"Không thể xóa {img_path} hoặc {label_path}.\nLỗi: {e}")

        # Lưu các ảnh không được chọn vào confirmed.txt
        save_confirmed_images(to_keep)

        # Tải lại ảnh mới từ folder mà không trùng với confirmed_images
        self.images_and_labels = load_images_and_labels()

        # Xóa mảng selected_images sau khi chuyển tab
        self.selected_images.clear()

        # Xóa màn hình hiện tại và hiển thị ảnh mới
        self.display_images()

# Khởi chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()

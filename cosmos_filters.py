import os
import threading
from tkinter import *
from PIL import Image, ImageFilter, ImageOps, ImageTk

def process_image(input_image, output_folder, filters):
    try:
        image = Image.open(input_image)

        for filter_function, params in filters:
            image = filter_function(image, *params)

        _, filename = os.path.split(input_image)

        output_path = os.path.join(output_folder, f"{filename}")

        image.save(output_path)
        print(f"Saved: {output_path}")
    except Exception as e:
        print(f"Error processing {input_image}: {e}")

def apply_sepia_effect(image, intensity):
    sepia_image = ImageOps.colorize(image.convert('L'), "#704214", "#C0A080")
    blended_image = Image.blend(image, sepia_image, intensity)
    return blended_image

def resize_image(image, scale_percent):
    width, height = image.size
    new_width = int(width * scale_percent / 100)
    new_height = int(height * scale_percent / 100)
    new_size = (new_width, new_height)
    resized_image = ImageOps.fit(image, new_size)
    return resized_image

def apply_blur(image, radius):
    return image.filter(ImageFilter.GaussianBlur(radius))

def apply_sharp(image, factor):
    return image.filter(ImageFilter.UnsharpMask(radius=2, percent=int(factor*100), threshold=1))

def apply_edge(image, factor):
    enhanced_image = image.filter(ImageFilter.EDGE_ENHANCE)
    final_image = Image.blend(image, enhanced_image, factor)
    return final_image

def clear_output_folder(output_folder):
    for file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error clearing {output_folder}: {e}")


def main():
    input_folder = "input_images_folder"
    output_folder = "output_images_folder"
    input_images = [os.path.join(input_folder, filename) for filename in os.listdir(input_folder) if
                    filename.endswith(('.jpg', '.jpeg', '.png'))]

    clear_output_folder(output_folder)

    window = Tk()
    window.geometry("800x400")
    window.title("Image Filter App")

    filters_frame = Frame(window)
    filters_frame.pack(side=LEFT, padx=20)

    result_frame = Frame(window)
    result_frame.pack(side=RIGHT, padx=20)

    Label(filters_frame, text="Select Filters", font=("Helvetica", 12, "bold")).pack(pady=10)
    def update_preview_1(a):
        # Получаем первый путь к изображению из списка
        input_image = input_images[0] if input_images else None

        if input_image:
            # Загружаем изображение
            preview_image = Image.open(input_image)

            # Применяем фильтры с текущими значениями ползунков
            selected_filters = [
                (apply_sepia_effect, (sepia_var.get(),)),
                (resize_image, (resize_var.get(),)),
                (apply_blur, (blur_var.get(),)),
                (apply_sharp, (sharp_var.get(),)),
                (apply_edge, (edge_var.get(),))
            ]

            for filter_function, params in selected_filters:
                preview_image = filter_function(preview_image, *params)

            # Преобразуем изображение в PhotoImage и обновляем Label
            photo = ImageTk.PhotoImage(preview_image)
            preview_label.config(image=photo)
            preview_label.image = photo
    def apply_and_process():
        clear_output_folder(output_folder)

        sepia_intensity = sepia_var.get()
        resize_scale = resize_var.get()
        blur_radius = blur_var.get()
        sharp_factor = sharp_var.get()
        edge_factor = edge_var.get()

        selected_filters = []
        if sepia_intensity != 0:
            selected_filters.append((apply_sepia_effect, (sepia_intensity,)))
        if resize_scale != 100:
            selected_filters.append((resize_image, (resize_scale,)))
        if blur_radius != 0:
            selected_filters.append((apply_blur, (blur_radius,)))
        if sharp_factor != 0:
            selected_filters.append((apply_sharp, (sharp_factor,)))
        if edge_factor != 0:
            selected_filters.append((apply_edge, (edge_factor,)))

        threads = []
        for input_image in input_images:
            thread = threading.Thread(target=process_image, args=(input_image, output_folder, selected_filters))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        Label(result_frame, text="Processing complete!", font=("Helvetica", 14, "bold")).pack(pady=20)
        update_preview_1(1)
    global sepia_var, resize_var, blur_var, sharp_var, edge_var
    sepia_var = DoubleVar()
    resize_var = IntVar()
    blur_var = DoubleVar()
    sharp_var = DoubleVar()
    edge_var = DoubleVar()

    sepia_slider = Scale(filters_frame, label="Sepia Intensity", variable=sepia_var, from_=0, to=1, resolution=0.01, orient=HORIZONTAL)

    sepia_slider.pack(anchor=W)

    resize_slider = Scale(filters_frame, label="Resize Scale (%)", variable=resize_var, from_=10, to=200,
                          orient=HORIZONTAL)
    resize_slider.set(100)  # Устанавливаем начальное значение в 100
    resize_slider.pack(anchor=W)

    blur_slider = Scale(filters_frame, label="Blur Radius", variable=blur_var, from_=0, to=2, resolution=0.01,
                        orient=HORIZONTAL)

    blur_slider.pack(anchor=W)

    sharp_slider = Scale(filters_frame, label="Sharpness Factor", variable=sharp_var, from_=0, to=2, resolution=0.01,
                         orient=HORIZONTAL)
    sharp_slider.pack(anchor=W)

    edge_slider = Scale(filters_frame, label="Edge Enhancement Factor", variable=edge_var, from_=0, to=2,
                        resolution=0.01, orient=HORIZONTAL)
    edge_slider.pack(anchor=W)
    global preview_label
    preview_label = Label(result_frame, text="Preview")
    preview_label.pack(pady=10)
    update_preview_1(1)
    apply_button = Button(filters_frame, text="Apply and Process", command=apply_and_process, font=("Helvetica", 12, "bold"))
    apply_button.pack(pady=20)



    # Обновляем предпросмотр при изменении значений ползунков
    sepia_slider.config(command=update_preview_1)
    resize_slider.config(command=update_preview_1)
    blur_slider.config(command=update_preview_1)
    sharp_slider.config(command=update_preview_1)
    edge_slider.config(command=update_preview_1)

    window.mainloop()

if __name__ == "__main__":
    main()

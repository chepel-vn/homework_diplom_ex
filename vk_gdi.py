import vk_common
from tkinter import *
from tkinter import messagebox as mb
from PIL import Image, ImageTk
from time import sleep
import vk_db


def set_button(frame, caption, func, number):
    """

    (object Frame, string, object function, int) -> (None)

    Function set button with caption on the frame

    """

    b = Button(frame, text=caption, width=15, height=1)
    b.bind("<Button-1>", lambda event, f=number: func(event, f))
    b.pack(side=LEFT)


class LikeImages:

    def __init__(self, users):
        if len(users) < 1:
            vk_common.dprint(1, "Ошибка с входными параметрами: массив пользователей пуст.")

        self.users = users
        vk_common.dprint(2, vk_common.func_name(), "Список пользователей при входе: ", self.users)
        self.top_id = 1
        self.label = None
        self.user_id = None
        self.item_ids = None
        self.top_images = None
        self.root = None
        self.f_source = None
        self.f_control = None
        self.f_image = None

    def load_image(self):
        """

        (None) -> (int)

        Function loads images from files from the disk to object label

        """

        if not hasattr(self, 'user_id'):
            vk_common.dprint(1, "Не определен атрибут user_id.")
            return -1

        if not hasattr(self, 'top_id'):
            vk_common.dprint(1, "Не определен атрибут top_id.")
            return -1

        if self.top_id not in (1, 2, 3):
            vk_common.dprint(1, "Атрибут top_id <> 1,2,3.")
            return -1

        err = -1
        try:
            vk_common.mk_dir(vk_common.DIR_IMAGES)
            file_path = f"{vk_common.DIR_IMAGES}{self.user_id}_{self.top_id}.jpg"
            vk_common.dprint(2, vk_common.func_name(), f"Загружаем фото на форму из файла {file_path}.")

            img = Image.open(file_path)
            render = ImageTk.PhotoImage(img)

            if hasattr(self, 'label'):
                if self.label is not None:
                    self.label.destroy()

            self.label = Label(self.f_image, image=render)
            self.label.image = render
            self.label.pack()

            err = 0
        except FileNotFoundError as error:
            vk_common.dprint(2, vk_common.func_name(), "Возникло исключение: ", error)
            err = -2
        finally:
            return err

    def select_user(self, number):
        """

        (int) -> (int)

        Function describes pressing on any button on the frame

        """

        if len(self.users) < 1:
            vk_common.dprint(1, "Массив пользователей пуст.")
            return -1

        vk_common.dprint(2, vk_common.func_name(), "Список пользователей при входе: ", self.users)
        self.user_id = self.users[number-1][0]
        self.item_ids = self.users[number-1][1]
        vk_common.dprint(2, f"Выбран пользователь с id = {self.user_id}")

        rows, err = vk_db.get_photo_info_by_user_id(self.user_id)
        if err != 0:
            vk_common.dprint(1, "Ошибка получения имен изображений.")
            return -2

        vk_common.dprint(2, rows)

        self.top_images = rows

        err = self.load_image()
        if err != 0:
            vk_common.dprint(1, "Ошибка при загрузке изображений из БД на форму")
            return -2

        return 0

    def select(self, event, number):
        """

        (string, int) -> (None)

        Function describes pressing on any button on the frame (event = press on button)

        """

        return self.select_user(number)

    def like(self, event, number):
        """

        (string, int) -> (None)

        Function describes pressing on button "LIKE" on the frame (event = press on button)

        """

        if not hasattr(self, 'user_id') or not hasattr(self, 'top_id'):
            vk_common.dprint(2, vk_common.func_name(), f"Не заданы атрибуты user_id = или top_id.")
            return

        item_id = self.item_ids[self.top_id-1]
        if item_id is None:
            vk_common.dprint(2, vk_common.func_name(), f"Атрибут item_id = None.")
            return
        else:
            vk_common.dprint(2, vk_common.func_name(), f"number = {number}; item_id = {item_id}")

        vk_common.dprint(1, f"имя файла с фото = \"{self.user_id}_{self.top_id}\"; "
                            f"ссылка = https://vk.com/id{self.user_id}")

        err, msg, likes = vk_common.like_photo(self.user_id, item_id)
        if err != 0:
            vk_common.dprint(2, "Не смогли поставить лайк.")
            mb.showinfo("Информация", f"Не смогли поставить лайк фото пользователя c id = {self.user_id}.")
            return
        vk_common.dprint(2, f"Поставили лайк: owner_id = {self.user_id}; item_id = {item_id}")
        mb.showinfo("Информация", f"Поставили лайк фото пользователя c id = {self.user_id}.")
        # err, msg, likes = user.like_photo(234068204, 345376029)

    def dislike(self, event, number):
        """

        (string, int) -> (None)

        Function describes pressing on button "DISLIKE" on the frame (event = press on button)

        """

        if not hasattr(self, 'user_id') or not hasattr(self, 'top_id'):
            vk_common.dprint(2, vk_common.func_name(), f"Не заданы атрибуты user_id = или top_id.")
            return

        item_id = self.item_ids[self.top_id - 1]
        if item_id is None:
            vk_common.dprint(2, vk_common.func_name(), f"Атрибут item_id = None.")
            return
        else:
            vk_common.dprint(2, vk_common.func_name(), f"number = {number}; item_id = {item_id}")

        vk_common.dprint(2, vk_common.func_name(), f"number = {number}; item_id = {item_id}")
        vk_common.dprint(1, f"имя файла с фото = \"{self.user_id}_{self.top_id}\"; "
                            f"ссылка = https://vk.com/id{self.user_id}")

        err, msg, likes = vk_common.dislike_photo(self.user_id, item_id)
        if err != 0:
            mb.showinfo("Информация", f"Не смогли убрать лайк у фото пользователя с id = {self.user_id}.")
            vk_common.dprint(2, "Не смогли убрать лайк.")
            return
        mb.showinfo("Информация", f"Убрали лайк у фото пользователя с id = {self.user_id}.")
        vk_common.dprint(2, f"Убрали лайк: owner_id = {self.user_id}; item_id = {item_id}")

    def left(self, event, number):
        """

        (string, int) -> (int)

        Function describes pressing on button "<<" on the frame (event = press on button)

        """

        if not hasattr(self, 'top_images'):
            vk_common.dprint(1, "Не определен атрибут \"top_images\".")
            return -1

        if len(self.top_images) < 1:
            vk_common.dprint(1, "Массив изображений пуст.")
            return -1

        while True:
            self.top_id -= 1
            if self.top_id < 1:
                self.top_id = 3
            err = self.load_image()
            if err == 0:
                break
        return 0

    def right(self, event, number):
        """

        (string, int) -> (int)

        Function describes pressing on button ">>" on the frame (event = press on button)

        """

        if not hasattr(self, 'top_images'):
            vk_common.dprint(1, "Не определен атрибут \"top_images\".")
            return -1

        if len(self.top_images) < 1:
            vk_common.dprint(1, "Массив изображений пуст.")
            return -1

        while True:
            self.top_id += 1
            if self.top_id > 3:
                self.top_id = 1
            err = self.load_image()
            if err == 0:
                break
        return 0

    def execute_app(self):
        """

        (None) -> (None)

        Function describes execute gdi interface for liking or disliking photos of users

        """

        self.root = Tk()
        self.root.geometry(f"{vk_common.MAX_IMAGE_WIDTH}x{vk_common.MAX_IMAGE_HEIGHT}")
        self.root.title("Лайкер")

        self.f_source = Frame(self.root)
        self.f_source.pack(side=TOP)

        self.f_control = Frame(self.root)
        self.f_control.pack(side=TOP)

        self.f_image = Frame(self.root)
        self.f_image.pack(side=BOTTOM)

        vk_common.dprint(2, vk_common.func_name(), "Список пользователей при входе: ", self.users)
        for number, user in enumerate(self.users, 1):
            set_button(self.f_source, str(number), self.select, number)

        set_button(self.f_control, "Лайкнуть", self.like, 1)
        set_button(self.f_control, "ДизЛайкнуть", self.dislike, 2)
        set_button(self.f_control, "<<", self.left, 3)
        set_button(self.f_control, ">>", self.right, 4)

        self.top_id = 1
        self.select_user(1)

        self.root.focus_set()
        self.root.wm_state('zoomed')
        self.root.call('wm', 'attributes', '.', '-topmost', '1')
        self.root.mainloop()
        sleep(1/3)
        self.root.quit()

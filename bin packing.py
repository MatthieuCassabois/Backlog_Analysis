import string


class Rectangle:
    current_char_index = 0
    available_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.char = Rectangle.available_chars[Rectangle.current_char_index]
        Rectangle.current_char_index += 1
        if Rectangle.current_char_index >= len(Rectangle.available_chars):
            raise ValueError("Not enough unique characters for rectangles")


class Bin:
    def __init__(self):
        self.placed_rectangles = []  # List of placed rectangles (x, y, width, height, char)
        self.skyline = [(0, 0)]  # List of (x, y) tuples representing the skyline
        self.max_width = 0
        self.max_height = 0

    def can_place_rectangle(self, rect, position):
        x, y = position
        if x + rect.width > self.max_width:
            self.max_width = x + rect.width
        if y + rect.height > self.max_height:
            self.max_height = y + rect.height

        for (px, py, pw, ph, _) in self.placed_rectangles:
            if not (x + rect.width <= px or x >= px + pw or y + rect.height <= py or y >= py + ph):
                return False
        return True

    def update_skyline(self, rect, position):
        x, y = position
        new_skyline = []
        i = 0
        while i < len(self.skyline) and self.skyline[i][0] < x:
            new_skyline.append(self.skyline[i])
            i += 1

        new_skyline.append((x, y + rect.height))
        end_x = x + rect.width

        while i < len(self.skyline) and self.skyline[i][0] < end_x:
            i += 1

        if i < len(self.skyline) and self.skyline[i][0] == end_x:
            new_skyline.append((end_x, self.skyline[i][1]))
            i += 1
        else:
            new_skyline.append((end_x, y))

        new_skyline.extend(self.skyline[i:])
        self.skyline = new_skyline

    def find_position_for_new_rectangle(self, rect):
        best_position = None
        best_height = float('inf')

        for i in range(len(self.skyline) - 1):
            x, y = self.skyline[i]
            if x + rect.width <= self.skyline[i + 1][0]:
                if y + rect.height < best_height:
                    best_height = y + rect.height
                    best_position = (x, y)

        if best_position is None:
            x, y = self.skyline[-1]
            best_position = (x, y)

        return best_position

    def place_rectangle(self, rect, position):
        if self.can_place_rectangle(rect, position):
            self.placed_rectangles.append((position[0], position[1], rect.width, rect.height, rect.char))
            self.update_skyline(rect, position)
            return True
        return False

    def draw_ascii(self):
        grid = [[' ' for _ in range(self.max_width)] for _ in range(self.max_height)]

        for (x, y, w, h, char) in self.placed_rectangles:
            for i in range(y, y + h):
                for j in range(x, x + w):
                    grid[i][j] = char

        ascii_art = "\n".join(["".join(row) for row in grid])
        print(ascii_art)


def rectangle_packing(rectangles):
    rectangles.sort(key=lambda rect: (rect.height, rect.width), reverse=True)

    bin = Bin()

    for rect in rectangles:
        position = bin.find_position_for_new_rectangle(rect)
        bin.place_rectangle(rect, position)

    return bin


# Liste des rectangles
rectangles = [
    Rectangle(1, 1),
    Rectangle(2, 1),
    Rectangle(2, 1),
    Rectangle(3, 1),
    Rectangle(3, 1),
    Rectangle(4, 2),
    Rectangle(3, 1),
    Rectangle(3, 1),
    Rectangle(3, 1),
    Rectangle(4, 2),
    Rectangle(1, 1),
    Rectangle(5, 1),
Rectangle(3, 1)
]

# Emballer les rectangles dans le bin
bin = rectangle_packing(rectangles)
# Dessiner le résultat en ASCII
bin.draw_ascii()

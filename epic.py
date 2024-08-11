import re
from math import ceil
from typing import Tuple, Iterable

from story import Story, cut_text_into_rectangles

NB_LINES = 6
RECT_HEIGHT = 1


class Epic(object):
    def __init__(self, name: str, stories: Tuple[Story] = tuple()):
        self.name = name
        self.stories = stories

    def add_story(self, story):
        self.stories = self.stories + (story,)

    def get_epic_priority_from_name(self):
        match = re.findall(r"^\[P(.*)]", self.name)
        if match:
            return float(match[0])
        else:
            return float("inf")

    def get_total_estimate(self):
        return sum([story.estimate for story in self.stories])

    def get_non_nul_stories(self):
        return [story for story in self.stories if story.estimate]


def pretty_print_ascii_epics(epics: Iterable[Epic]):
    all_stories = []
    for epic in epics:
        all_stories += epic.get_non_nul_stories()

    max_width_for_1 = ceil(max(story.get_char_weight(nb_lines=NB_LINES) for story in all_stories) * 1.2)

    for epic in epics:
        epic_stories = sorted(epic.get_non_nul_stories(), key=lambda story: story.estimate, reverse=True)

        print(f" {epic.name} ".center(150, "¤"))
        first_story = epic_stories[0]

        biggest_weight = first_story.estimate
        stories_grid = [[first_story]]
        for story in epic_stories[1:]:
            for i_line, line in enumerate(stories_grid):
                if sum([story.estimate for story in line]) + story.estimate <= biggest_weight:
                    stories_grid[i_line] = stories_grid[i_line] + [story]
                    break
            else:
                stories_grid.append([story])
        for line in stories_grid:
            blocs = [story.pretty_print_ascii_weighted(max_width_for_1, nb_lines=NB_LINES) for story in line]
            for bloc_line in zip(*blocs):
                print("".join(bloc_line))


def pretty_print_epics(epics: Iterable[Epic]):
    class StoryRectangle(object):

        def __init__(self, text, width, x_pos, y_pos):
            self.text = text
            self.width = width
            self.x_pos = x_pos
            self.y_pos = y_pos

    all_stories = []
    for epic in epics:
        all_stories += epic.get_non_nul_stories()

    max_width_for_1 = ceil(max(story.get_char_weight(nb_lines=NB_LINES) for story in all_stories) * 1.2)

    for epic in epics:
        epic_stories = sorted(epic.get_non_nul_stories(), key=lambda story: story.estimate, reverse=True)

        first_story = epic_stories[0]

        biggest_weight = first_story.estimate
        stories_grid = [[first_story]]
        for story in epic_stories[1:]:
            for i_line, line in enumerate(stories_grid):
                if sum([story.estimate for story in line]) + story.estimate <= biggest_weight:
                    stories_grid[i_line] = stories_grid[i_line] + [story]
                    break
            else:
                stories_grid.append([story])

        story_squares = []
        for i_line, line in enumerate(stories_grid):
            line_origine = 0
            for story in line:
                story_squares.append(StoryRectangle(cut_text_into_rectangles(story.name,
                                                                             width=max_width_for_1 * story.estimate - 2,
                                                                             max_height=NB_LINES),
                                                    story.estimate,
                                                    x_pos=line_origine,
                                                    y_pos=i_line * RECT_HEIGHT
                                                    )
                                     )
                line_origine += story.estimate

    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties

    def get_text_dimensions(text, font_size):
        """
        Calcule les dimensions du texte pour une taille de police donnée.

        Parameters:
        text (list(str)): Le texte dont les dimensions doivent être calculées.
        font_size (int): La taille de la police.

        Returns:
        (float, float): La largeur et la hauteur du texte.
        """
        font = FontProperties(size=font_size)

        max_width = 0
        total_height = 0
        for line in text:
            text_path = TextPath((0, 0), line, prop=font)
            bounds = text_path.get_extents()
            max_width = max(max_width, bounds.width)
            total_height += bounds.height
        return max_width, total_height

    def draw_rectangle_with_text(ax, x, y, width, height, text):
        """
        Dessine un rectangle à une position donnée avec du texte ajusté à l'intérieur.

        Parameters:
        ax (matplotlib.axes.Axes): L'axe sur lequel dessiner le rectangle.
        x (float): La position x du coin inférieur gauche du rectangle.
        y (float): La position y du coin inférieur gauche du rectangle.
        width (float): La largeur du rectangle.
        height (float): La hauteur du rectangle.
        text (str): Le texte à afficher à l'intérieur du rectangle.
        """
        # Ajouter le rectangle
        rect = Rectangle((x, y), width, height, linewidth=1, edgecolor='black', facecolor='none')
        ax.add_patch(rect)

        # Ajuster le texte pour qu'il prenne le plus de place possible sans dépasser
        font_size = 20

        while font_size > 2:
            width_needed, height_needed = get_text_dimensions(text, font_size)
            if width_needed >= width or height_needed >= height:
                font_size //= 1.2
            else:
                break
        # Ajouter le texte
        ax.text(x + width / 2, y + height / 2, text, fontsize=font_size, ha='center', va='center')

    # Création de la figure et des axes
    fig, ax = plt.subplots()

    # Ajustement des limites des axes
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)

    # Dessin des rectangles avec le texte
    for rect in story_squares:
        print(rect.text)
        draw_rectangle_with_text(ax, rect.x_pos, rect.y_pos, rect.width, RECT_HEIGHT, "\n".join(rect.text))

    # Affichage
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

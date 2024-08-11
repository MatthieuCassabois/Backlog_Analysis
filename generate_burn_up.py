import argparse
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from Shortcut_Extract_Loader import ShortcutExtractLoader
from story import to_date_or_none

DEFAULT_FILE_PATH = Path(
    "C:\\Users\\Matthieu CASSABOIS\\Documents\\suivi_CEVA\\archives\\space-6761-exported-at-20240724T1227+0000.csv")

DEFAULT_CATEGORY_TO_DISCRIMINATE = "priority"
DEFAULT_CATEGORIES = ["", "Highest", "High", "Medium", "Low", "Lowest"]


def get_all_stories_min_created_at_and_categories(epics, category_to_discriminate):
    all_stories = []
    min_created_at = datetime.now()
    all_categories = set()
    for epic in epics:
        stories = epic.stories
        for story in stories:
            if story.created_at < min_created_at:
                min_created_at = story.created_at
            all_categories.add(getattr(story, category_to_discriminate))
        all_stories += stories

    return all_stories, min_created_at, sorted(all_categories)


def get_period_end(date, period_len, min_created_at):
    """
    Fonction pour obtenir la date de début d'itération correspondant à une date
    :param date: date que l'on souhaite localiser
    :param period_len: durée de l'itération
    :param min_created_at: date de début de la première itération
    :return:
    """
    period_len = timedelta(days=period_len)
    return date - (date - min_created_at) % period_len + period_len


def get_burnup(file_path=DEFAULT_FILE_PATH,
               category_to_desriminate=DEFAULT_CATEGORY_TO_DISCRIMINATE,
               categories_in_order=DEFAULT_CATEGORIES,
               min_date=None
               ):


    shortcut_loader = ShortcutExtractLoader(file_path)
    epics = shortcut_loader.load()

    all_stories, min_created_at, all_categories = get_all_stories_min_created_at_and_categories(epics,
                                                                                                category_to_desriminate)

    if min_date is None:
        min_date = min_created_at

    if not categories_in_order:
        categories_in_order = all_categories

    period_data = defaultdict(lambda: defaultdict(lambda: {'open': 0, 'done': 0}))

    for story in all_stories:
        story_category = getattr(story, category_to_desriminate)
        created_period_start = get_period_end(story.created_at, period_len=14, min_created_at=min_date)

        # Mise à jour des "open" (estimations créées)
        period_data[created_period_start][story_category]['open'] += story.estimate if story.estimate else 0

        # Mise à jour des "done" (estimations réalisées) si la story est complétée
        if story.is_completed and story.completed_at is not None:
            completed_period_start = get_period_end(story.completed_at, period_len=14, min_created_at=min_date)
            period_data[completed_period_start][story_category]['done'] += story.estimate if story.estimate else 0

    return period_data, categories_in_order


def print_burnup_for_excel(burnup_data, categories_in_order):
    """
    Print une ligne pour chaque itération, avec tout les done pour chaque catégorie, puis tout les open
    :param burnup_data:
    :return:
    """
    print("\t".join([""] +
                    list(map(lambda s: s+" (done)", categories_in_order)) +
                    list(map(lambda s: s+" (total)", categories_in_order))))

    for period, categories_dict in sorted(burnup_data.items()):
        line = [str(period)]
        for state in ["done", "open"]:
            for category in categories_in_order:
                line.append(str(categories_dict[category][state]))
        print("\t".join(line))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that return burn up infos from a csv source")

    # Ajout des arguments
    parser.add_argument("file_path", type=str, help="the path of the csv file.")
    parser.add_argument("--category", type=str, help="The category on which discriminate")
    parser.add_argument("--category_order", type=str, help="The list of the categories, in the ordre we want it")
    parser.add_argument("--min_date", type=str, help="Date of the first iteration's start")

    args = parser.parse_args()

    file_path = args.file_path
    category = args.category if args.category else DEFAULT_CATEGORY_TO_DISCRIMINATE
    categories_in_order = args.category_order if args.category else DEFAULT_CATEGORIES
    min_date = args.min_date if args.min_date else None
    min_date = to_date_or_none(min_date)

    burnup_data, categories_in_order = get_burnup(file_path, category, categories_in_order, min_date)

    print_burnup_for_excel(burnup_data, categories_in_order)


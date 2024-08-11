import csv

from epic import Epic
from story import Story


class ShortcutExtractLoader(object):

    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        epics = []
        with (open(self.file_path, 'r', encoding='utf-8') as file):
            csv_file = csv.reader(file)
            first_line = True
            for line in csv_file:
                if first_line:
                    first_line = False
                    continue
                story = Story.from_shortcut_csv(line)
                if not story.is_archived:
                    if story.epic_name not in [epic.name for epic in epics]:
                        new_epic = Epic(story.epic_name)
                        new_epic.add_story(story)
                        epics.append(new_epic)
                    else:
                        epic = [epic for epic in epics if epic.name == story.epic_name][0]
                        epic.add_story(story)

        return epics
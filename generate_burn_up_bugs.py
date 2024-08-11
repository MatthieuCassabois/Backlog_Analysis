from datetime import datetime, timedelta
from pathlib import Path

from Shortcut_Extract_Loader import ShortcutExtractLoader

file_path = Path(
    "C:\\Users\\Matthieu CASSABOIS\\Documents\\suivi_CEVA\\bugs\\space-6756-exported-at-20240722T0956+0000.csv")

shortcut_loader = ShortcutExtractLoader(file_path)
epics = shortcut_loader.load()

epics = sorted(epics, key=lambda epic: (epic.get_epic_priority_from_name(), epic.name))
all_stories = []
for epic in epics:
    all_stories += epic.stories

min_created_at = datetime.now()


for story in all_stories:
    if story.created_at < min_created_at:
        min_created_at = story.created_at

period_len = timedelta(days=14)
period_start = min_created_at
open_by_period = {}
done_by_period = {}
while period_start <= datetime.now():
    open_by_period[period_start] = 0
    done_by_period[period_start] = 0
    period_start += period_len

for story in all_stories:
    for period_start in open_by_period.keys():
        if period_start <= story.created_at < period_start + period_len:
            open_by_period[period_start] += 1
        if (story.completed_at is not None and
                period_start <= story.completed_at < period_start + period_len):
            done_by_period[period_start] += 1
            break


print("date\tbug créés\tbug résolus")
for period_start in sorted(done_by_period.keys()):
    print(f"{period_start + period_len}\t{open_by_period[period_start]}\t{done_by_period[period_start]}")

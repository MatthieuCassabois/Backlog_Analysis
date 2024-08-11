import re
from datetime import datetime
from math import ceil


def cut_text_into_rectangles(text, width, max_height):
    def cut_text_into_x_lines(text, nb_lines):

        words = text.split()

        avg_len = ceil(len(text) / nb_lines)
        lines = []
        current_line = []
        current_len = 0
        for word in words:
            if current_len + len(current_line) + len(word) > avg_len and current_line:
                lines.append(' '.join(current_line))
                current_line = []
                current_len = 0
            current_line.append(word)
            current_len += len(word)

        # Append the last line
        if current_line:
            if len(lines) == max_height:
                lines[-1] = lines[-1] + " " + ' '.join(current_line)
            else:
                lines.append(' '.join(current_line))

        return lines

    new_text = [text]
    nb_lines = 2
    while max([len(line) for line in new_text]) > width - 2:  # -2 pour les caractères |
        new_text = cut_text_into_x_lines(text, nb_lines)
        if nb_lines >= max_height:
            raise Exception(
                f"Peux pas rentrer le text suivant dans du {width} de large et en {max_height} de haut.\n{text}")
        nb_lines += 1
    return new_text

def to_date_or_none(str_date):
    date = None
    if str_date:
        date = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S')
    return date

class Story(object):
    def __init__(self, story_id=None, name: str = None, story_type=None, requester=None, owners=None, description=None,
                 is_completed=None, created_at=None, started_at=None, updated_at=None, moved_at=None, completed_at=None,
                 estimate=None, external_ticket_count=None, external_tickets=None, is_blocked=None, is_a_blocker=None,
                 due_date=None, labels=None, epic_labels=None, tasks=None, state=None, epic_id=None, epic=None,
                 project_id=None, project=None, iteration_id=None, iteration=None, utc_offset=None, is_archived=None,
                 team_id=None, team=None, epic_state=None, epic_is_archived=None, epic_created_at=None,
                 epic_started_at=None, epic_due_date=None, milestone_id=None, milestone=None, milestone_state=None,
                 milestone_created_at=None, milestone_started_at=None, milestone_due_date=None,
                 milestone_categories=None, epic_planned_start_date=None, workflow=None, workflow_id=None,
                 priority=None, severity=None, product_area=None, skill_set=None, technical_area=None,
                 custom_fields=None, acceptance_criteria=None):
        self.story_id = story_id
        self.name = name
        self.story_type = story_type
        self.requester = requester
        self.owners = owners
        self.description = description
        self.is_completed = is_completed == "true"
        self.created_at = to_date_or_none(created_at)
        self.started_at = to_date_or_none(started_at)
        self.updated_at = to_date_or_none(updated_at)
        self.moved_at = to_date_or_none(moved_at)
        self.completed_at = to_date_or_none(completed_at)
        try:
            self.estimate = int(estimate)
        except ValueError:
            self.estimate = None
        self.external_ticket_count = external_ticket_count
        self.external_tickets = external_tickets
        self.is_blocked = is_blocked.startswith("t")
        self.is_a_blocker = is_a_blocker.startswith("t")
        self.due_date = to_date_or_none(due_date)
        self.labels = labels
        self.epic_labels = epic_labels
        self.tasks = tasks
        self.state = state
        self.epic_id = epic_id
        self.epic_name = epic
        self.project_id = project_id
        self.project = project
        self.iteration_id = iteration_id
        self.iteration = iteration
        self.utc_offset = utc_offset
        self.is_archived = is_archived.startswith("t")
        self.team_id = team_id
        self.team = team
        self.epic_state = epic_state
        self.epic_is_archived = epic_is_archived.startswith("t")
        self.epic_created_at = to_date_or_none(epic_created_at)
        self.epic_started_at = to_date_or_none(epic_started_at)
        self.epic_due_date = to_date_or_none(epic_due_date)
        self.milestone_id = milestone_id
        self.milestone = milestone
        self.milestone_state = milestone_state
        self.milestone_created_at = to_date_or_none(milestone_created_at)
        self.milestone_started_at = to_date_or_none(milestone_started_at)
        self.milestone_due_date = to_date_or_none(milestone_due_date)
        self.milestone_categories = milestone_categories
        self.epic_planned_start_date = to_date_or_none(epic_planned_start_date)
        self.workflow = workflow
        self.workflow_id = workflow_id
        self.priority = priority
        self.severity = severity
        self.product_area = product_area
        self.skill_set = skill_set
        self.technical_area = technical_area
        self.custom_fields = custom_fields
        self.acceptance_criteria = acceptance_criteria

    @classmethod
    def from_shortcut_csv(cls, line):
        story = cls(*line)
        story.set_acceptance_criteria_from_desc()
        return story

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def set_acceptance_criteria_from_desc(self):
        acceptance_criterias = re.findall(r'critères? d\'accepta\w*(.*?)(?=(?:[^"]",)|(?:^##))',
                                          self.description, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        new_acceptance_criterias = "\n".join(acceptance_criterias)
        new_acceptance_criterias = re.sub(r'- \[ ]\s*\n', r'', new_acceptance_criterias)
        new_acceptance_criterias = re.sub(r'\n\n\n+', r'\n\n', new_acceptance_criterias)

        if new_acceptance_criterias.strip():
            self.acceptance_criteria = new_acceptance_criterias

    def get_char_weight(self, nb_lines):
        """
        Pour pouvoir faire un pretty print avec d'autre US,
        Retourne le "poid" qu'un caractère du nom de l'US représenterai,
        en partant du principe qu'il aurai la forme suivante :
        [
         nom
          de
         l'us
             ]
        Exemple :
         nom : "Af peut faire un truc" (len 21)
         estimate : 8
         retourne char_weight = 8/23
        :return: float
        """
        return (2 + len(self.name) // (nb_lines - 1)) / self.estimate

    def pretty_print_ascii_weighted(self, nb_char_for_1, nb_lines):
        """
        Retourne un texte formater pour contenir le nom et
         prendre la place en fonction de la taille donné et de l'estimate.
        Par exemple :
        name = "ABC"
        estimate = 2
        nb_char_for_1 = 5
        return : "[   ABC  ]" (longueur 10)
        :param nb_char_for_1 : int, la taille minimum que un 1 doit prendre pour représenter toute les US
        :return:
        """

        cut_name = cut_text_into_rectangles(self.name,
                                            width=nb_char_for_1 * self.estimate - 2,
                                            max_height=nb_lines)

        append_after = True
        while len(cut_name) < nb_lines:
            if append_after:
                cut_name.append("")
            else:
                cut_name = [""] + cut_name
            append_after = not append_after

        line_len = nb_char_for_1 * self.estimate - 2  # 2 pour remettre les crochets à la fin

        drawned_lines = ["╭" + "-" * line_len + "╮"]
        for line in cut_name:
            drawned_lines.append("|" + line.center(line_len, ("#" if self.is_completed else " ")) + "|")
        drawned_lines.append("╰" + "-" * line_len + "╯")

        return drawned_lines

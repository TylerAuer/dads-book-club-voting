import dataclasses
import csv
import itertools

from os import path
from typing import Dict, Final, List, Set, Tuple

BookTitles = Set[str]

# Fewest number of people allowed in a group 
_MIN_GROUP_SIZE: Final[int] = 3
# Path to the CSV file containing the form responses
_PATH_TO_FORM_RESPONSES: Final[str] = path.join('form_responses','book-2.csv')
# Colums in the CSV file to find each piece of data
_FIRST_NAME_COLUMN_IDX: Final[int] = 3
_LAST_NAME_COLUMN_IDX: Final[int] = 4
_BOOK_PREFS_COLUMN_IDX: Final[int] = 6


@dataclasses.dataclass()
class UserPreference:
    first_name: str
    last_name: str
    books_by_preference: List[str]

    @staticmethod
    def from_csv_row(row: List[str]) -> "UserPreference":
        books_raw = row[_BOOK_PREFS_COLUMN_IDX].split(",")
        books_cleaned = [book.strip() for book in books_raw]
        return UserPreference(
            first_name=row[_FIRST_NAME_COLUMN_IDX],
            last_name=row[_LAST_NAME_COLUMN_IDX],
            books_by_preference=books_cleaned,
        )
    
    def get_rank_of_book(self, book: str) -> int:
        for rank, b in enumerate(self.books_by_preference):
            if b == book:
                return rank + 1
        raise ValueError(f"Book {book} not found in user preferences")

    def get_pretty_name(self) -> str:
        return f"{self.first_name} {self.last_name[0]}"


@dataclasses.dataclass()
class ComboSummary:
    books: BookTitles
    book_to_user_pref: Dict[str, List[UserPreference]]
    avg_score: float = dataclasses.field(init=False)
    harmonic_mean: float = dataclasses.field(init=False)
    root_mean_square: float = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        avg_running_sum = 0
        harmonic_running_sum = 0
        squared_running_sum = 0
        score_count = 0
        for book, user_prefs in self.book_to_user_pref.items():
            for user_pref in user_prefs:
                user_score = user_pref.get_rank_of_book(book)
                
                avg_running_sum += user_score
                harmonic_running_sum +=  1 / user_score
                squared_running_sum += user_score ** 2
                score_count += 1

        
        self.avg_score = avg_running_sum / score_count
        self.harmonic_mean = score_count / harmonic_running_sum
        self.root_mean_square = (squared_running_sum / score_count) ** 0.5
    
    @staticmethod
    def from_books_and_user_prefs(
        books: BookTitles, user_prefs: List[UserPreference]
    ) -> "ComboSummary":
        book_to_user_pref = {book: [] for book in books}
        for user_pref in user_prefs:
            for preferred_book in user_pref.books_by_preference:
                if preferred_book in books:
                    book_to_user_pref[preferred_book].append(user_pref)
                    break
        return ComboSummary(books, book_to_user_pref)
    
    @property
    def title_list(self, max_title_len: int = 12) -> str:
        """
        Return a string representation of the book titles in the combo summary.
        """
        return ", ".join(
            [book[:max_title_len].rstrip() for book in self.books]
        ) + "..." if len(self.books) > max_title_len else ", ".join(self.books)
        


def run():
    user_prefs = _load_csv()
    book_titles = _get_all_book_titles(user_prefs)
    book_combos = _combinations_for_all_book_counts(book_titles)
    combo_summaries = generate_combo_summaries(user_prefs, book_combos)
    valid_combo_summaries = filter_invalid_summaries(combo_summaries)
    sorted_combo_summaries = sorted(
        valid_combo_summaries, 
        # Sort from smallest to largest by avg_score and then by the number of books (fewest first)
        key=lambda x: (x.root_mean_square, len(x.books))
    )
    print_results(
        user_prefs,
        book_titles,
        book_combos,
        valid_combo_summaries,
        sorted_combo_summaries,
    )

def _load_csv() -> Tuple[List[UserPreference], BookTitles]:
    """
    Load the CSV file and return a list of UserPreference objects.
    """
    with open(_PATH_TO_FORM_RESPONSES, newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        user_prefs = [
            UserPreference.from_csv_row(row) for row in reader
        ]
    return user_prefs

def _get_all_book_titles(user_prefs: List[UserPreference]) -> BookTitles:
    books: BookTitles = set()
    for user_pref in user_prefs:
        books.update(user_pref.books_by_preference)
    return books
    

def _combinations_for_all_book_counts(books: BookTitles) -> List[BookTitles]:
    """
    Get all combinations of books choosing 1 book, then 2 books, etc. up to n books where n is the 
    number of books.
    """
    book_combinations: List[BookTitles] = []
    for i in range(1, len(books) + 1):
        book_combinations.extend(
            set(itertools.combinations(books, i))
        )
    return book_combinations

def generate_combo_summaries(
    user_prefs: List[UserPreference], book_combos: List[BookTitles]
) -> List[ComboSummary]:
    """
    Generate a list of ComboSummary objects for each combination of books.
    """
    combo_summaries = []
    for combo in book_combos:
        combo_summary = ComboSummary.from_books_and_user_prefs(
            combo, user_prefs
        )
        combo_summaries.append(combo_summary)
    return combo_summaries

def filter_invalid_summaries(
    combo_summaries: List[ComboSummary]
) -> List[ComboSummary]:
    """
    Filter out any combinations that do not have at least the minimum number of people to discuss
    the book.
    """
    filter_count = 0
    valid_combo_summaries = []
    for combo_summary in combo_summaries:
        if all(len(user_prefs) >= _MIN_GROUP_SIZE for user_prefs in combo_summary.book_to_user_pref.values()):
            valid_combo_summaries.append(combo_summary)
        else:
            filter_count += 1

    print(f"Filtered {filter_count} invalid combinations")
    return valid_combo_summaries

def print_results(
    user_prefs: List[UserPreference],
    book_titles: BookTitles,
    book_combos: List[BookTitles],
    combo_summaries: List[ComboSummary],
    sorted_combo_summaries: List[ComboSummary],
):
    print("Dad's Book Club Book Selection Results")
    print()
    print(f'Found optimal book selection(s) for {len(user_prefs)} people and {len(book_titles)} books.')
    print(f'Considered {len(book_combos)} different book combinations of which {len(combo_summaries)} had enough people in each group.')

    for i, combo in enumerate(sorted_combo_summaries[0:3]):
        print()
        print(f"#{i+1} - {combo.title_list}")
        print_combo_result(combo, prefix="  ")

def print_combo_result(book_combo: BookTitles, prefix: str = "  "):
    print(f"{prefix}{book_combo.root_mean_square:.2f} = Root Mean Square Rank")
    print(f"{prefix}{book_combo.harmonic_mean:.2f} = Geometric Mean Rank")
    print(f"{prefix}{book_combo.avg_score:.2f} = Arithmetic Mean Rank")
    print()

    for book in book_combo.books:
        users_for_book = book_combo.book_to_user_pref[book]
        users_with_book_rank = [
            f"{user.get_pretty_name()} ({user.get_rank_of_book(book)})"
            for user in users_for_book
        ]
        print(f"{prefix}{book}")
        for user_with_book_rank in users_with_book_rank:
            print(f"{prefix*2}{user_with_book_rank}")


if __name__ == "__main__":
    run()

from typing import Dict

# Application-memory storage dictionaries acting as temporary data repositories
db_books: Dict[int, dict] = {}
db_members: Dict[int, dict] = {}

# Counter state variables to auto-increment object record identifiers
book_id_counter: int = 1
member_id_counter: int = 1

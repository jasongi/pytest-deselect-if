# Changelog
## 0.1.3 2026-09-01
- support python 3.14
- drop python 3.9 (end of life)

## 0.1.2 2024-12-26
- support python 3.13

## 0.1.1 2024-03-24
- explicitly export deselect_if

## 0.1.0 2024-03-24
- initial release
- added deselect_if custom marker
- added `pytest_collection_modifyitems` to modify the collected items to deselect `Function` items when `deselect_if` returns True

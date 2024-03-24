# Changelog

## 0.1.1 2024-03-24
- explicitly export deselect_if

## 0.1.0 2024-03-24
- initial release
- added deselect_if custom marker
- added `pytest_collection_modifyitems` to modify the collected items to deselect `Function` items when `deselect_if` returns True

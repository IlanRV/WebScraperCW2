# WebScraperCW2

COMP3011 Coursework 2 search engine tool for https://quotes.toscrape.com/.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main
```

Planned commands:

```text
build
load
print <word>
find <query terms>
exit
```

## Testing

```bash
pytest --cov=src
```

## Project Structure

```text
src/      crawler, indexer, search logic, and CLI
tests/    unit tests for each component
data/     generated index file
```

# Employment appeal tribunal decisions

Scraping tribunal decision docs from [gov.uk](https://www.gov.uk/employment-appeal-tribunal-decisions) and making them super searchable


## Usage

- `make install` to install dependencies
- `make scrape_pdfs` to scrape pdfs from gov.uk
- `make parse_pdfs` to extract text from pdfs
- `make index` to index documents and concepts into elasticsearch
- `make api` to create an api for querying the indices

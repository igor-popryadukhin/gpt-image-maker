# gpt-image-maker

CLI utility for batch image generation using OpenAI's GPT Image API. The tool ingests a CSV-like text file with car metadata and source image URLs, constructs prompts from templates, downloads source images with retries, invokes the `gpt-image-1-mini` model, and writes transparent PNGs following the original URL path structure.

See [SPEC.md](SPEC.md) for the full technical requirements.

## Features
- CSV line parsing with configurable delimiters and column schemes.
- Prompt templating based on Python `str.format` placeholders.
- Resumable processing via state files tied to the input file hash.
- Resilient downloading and image generation with exponential backoff.
- Optional preview of before/after images.
- Structured logging and progress reporting using tqdm.

## Quickstart
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Prepare an input file matching the default column order (`brand, model, production_period, generation, body_type, image_url`) and a prompt template string or file.
3. Run the CLI (requires `OPENAI_API_KEY` in the environment):
   ```bash
   python -m gpt_image_maker.cli \
     --input-file data.txt \
     --output-root ./output \
     --prompt-template "{brand} {model} {production_period}, {body_type}, {generation} в боковом варианте на белом фоне. Фон строго прозрачный."
   ```

Use `--help` for the full list of options.

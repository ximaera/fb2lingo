# 📚 FB2Lingo — Bilingual FB2 Book Translator

**FB2Lingo** is a command-line tool that translates FB2 (FictionBook 2.0) ebooks into a bilingual format using the OpenAI API. It helps language learners by interleaving each paragraph with its translation — ideal for immersive reading and vocabulary building.

---

## ✨ Features

- 🔁 Translates FB2 books **paragraph by paragraph**
- 🌍 Supports **any language pair** (default: Russian ➡ Greek)
- ⚡ Faster translation with **parallel batch processing**
- 📄 Outputs a valid FB2 file with **interleaved paragraphs**
- 🔁 Customizable paragraph order (translation first or original first)
- 🧠 Powered by **OpenAI GPT models** (default: `gpt-4o-mini`, costs around $0.2-$0.5 to translate an entire book)

---

## 🛠 Installation

```bash
git clone https://github.com/ximaera/fb2lingo.git
cd fb2lingo
pip install -r requirements.txt
```

---

## 🔐 Prerequisites

Make sure your OpenAI API key is available as an environment variable:

```bash
export OPENAI_API_KEY=your-api-key-here
```

---

## 🚀 Usage

```
python3 fb2lingo.py input.fb2 output.fb2
```

### Options

| Flag               | Description                                        | Default          |
|--------------------|----------------------------------------------------|------------------|
| `--model`          | OpenAI model to use                                | `gpt-4o-mini`    |
| `--source`         | Source language                                    | `Russian`        |
| `--target`         | Target language                                    | `Greek`          |
| `--batch`          | Number of paragraphs per API request               | `100`            |
| `--threads`        | Number of threads for parallel batches             | `3`              |
| `--original-first` | Put the original paragraph **before** translation  | _disabled_       |
| `--footnotes`      | Put the original paragraph into footnotes          | _disabled_       |

---

## 📦 Examples

```
python3 fb2lingo.py heinlein_got_spacesuit_will_travel.fb2 heinlein_bilingual.fb2 \
  --source English \
  --target Spanish \
  --threads 4 \
  --batch 50 \
  --original-first
```

```
python3 fb2lingo.py homer_odyssey.fb2 homer_bilingual.fb2 \
  --source Greek \
  --target "English, proficiency level A2" \
  --batch 50
```

## 💡 Use Case

- 📘 Language learners reading native literature
- 📖 Side-by-side translation studies
- 📗 Creating bilingual educational material

---

## ⚠️ Disclaimer

- LLM (AI) tools do not work in a deterministic manner, sometimes parts of the book may be translated in a wrong way, some paragraphs might be omitted, etc. This script is sort of trying to handle this but doesn't go very far in this.
- This tool modifies the FB2 structure by inserting new paragraphs.
- Large books may require significant API tokens and time.
- Make sure to comply with OpenAI’s usage policies.

---

Special thanks to Robert A. Heinlein for providing a perfect debugging material.

---

## 📜 License

MIT © 2025 Töma Gavrichenkov, https://github.com/ximaera/fb2lingo

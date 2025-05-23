import os
import time
import argparse
from copy import deepcopy
from tqdm import tqdm
from lxml import etree
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

client = OpenAI()

def get_text(element):
    return ''.join(element.itertext()).strip()

def batch_translate(paragraphs, model, source_lang, target_lang):
    prompt = (
        f"Translate the following paragraphs from {source_lang} to {target_lang}. "
        f"Please only output the translated paragraphs. No explanations, comments, only the translated text. "
        f"Return the translations as numbered paragraphs (1., 2., etc.):\n\n"
    )
    for i, p in enumerate(paragraphs, 1):
        prompt += f"{i}. {p}\n"

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            lines = content.split('\n')
            translations = []
            current = ''
            for line in lines:
                if line.strip().startswith(tuple(f"{i}." for i in range(1, len(paragraphs)+1))):
                    if current:
                        translations.append(current.strip())
                    current = line.partition('.')[2].strip()
                else:
                    current += ' ' + line.strip()
            if current:
                translations.append(current.strip())

            if len(translations) != len(paragraphs):
                raise ValueError("Mismatch between source and translated paragraph count.")
            return translations
        except Exception as e:
            print(f"Retrying batch due to error: {e}")
            time.sleep(5 * (attempt + 1))

    raise RuntimeError("Batch translation failed after 3 attempts.")

def process_fb2_to_bilingual(input_path, output_path, model, src_lang, tgt_lang, batch_size, threads, original_first):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_path, parser)
    root = tree.getroot()

    nsmap = root.nsmap
    if None in nsmap:
        nsmap['fb2'] = nsmap.pop(None)

    paragraphs = root.xpath('//fb2:body//fb2:p', namespaces=nsmap)
    paragraph_batches = [paragraphs[i:i+batch_size] for i in range(0, len(paragraphs), batch_size)]

    def translate_batch(batch):
        texts = [get_text(p) for p in batch]
        return batch_translate(texts, model, src_lang, tgt_lang)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_batch = {
            executor.submit(translate_batch, batch): batch
            for batch in paragraph_batches
        }

        for future in tqdm(as_completed(future_to_batch), total=len(future_to_batch), desc="Translating"):
            batch = future_to_batch[future]
            try:
                translations = future.result()
                for orig_p, trans_text in zip(batch, translations):
                    trans_p = deepcopy(orig_p)
                    trans_p.clear()
                    trans_p.text = trans_text
                    parent = orig_p.getparent()
                    if original_first:
                        parent.replace(orig_p, orig_p)
                        orig_p.addnext(trans_p)
                    else:
                        parent.replace(orig_p, trans_p)
                        trans_p.addnext(orig_p)

            except Exception as e:
                print(f"Failed to process a batch: {e}")

    tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Create bilingual FB2 files using GPT.")
    parser.add_argument("input_file", help="Path to the input FB2 file.")
    parser.add_argument("output_file", help="Path to save the bilingual FB2 output.")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model (default: gpt-4o-mini)")
    parser.add_argument("--source", default="Russian", help="Source language (default: Russian)")
    parser.add_argument("--target", default="Greek", help="Target language (default: Greek)")
    parser.add_argument("--batch", type=int, default=100, help="Batch size (default: 100)")
    parser.add_argument("--threads", type=int, default=3, help="Number of threads for parallel translation (default: 3)")
    parser.add_argument("--original-first", action="store_true", help="Put original paragraph before the translation")

    args = parser.parse_args()

    process_fb2_to_bilingual(
        args.input_file,
        args.output_file,
        args.model,
        args.source,
        args.target,
        args.batch,
        args.threads,
        args.original_first
    )

    print(f"Translation complete. Output saved to: {args.output_file}")

if __name__ == "__main__":
    main()

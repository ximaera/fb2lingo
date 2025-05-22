import os
import argparse
from openai import OpenAI
from lxml import etree
from copy import deepcopy
from tqdm import tqdm
import time

client = OpenAI()

log = open("last.log", "w")

def batch_translate(paragraphs, model, source_lang, target_lang):
    prompt = (
        f"Translate the following paragraphs from {source_lang} to {target_lang}. "
        f"Please only output the translated paragraphs. No explanations, comments, only the translated text. "
        f"Return the translations as numbered paragraphs (1., 2., etc.):\n\n"
    )
    for i, p in enumerate(paragraphs, 1):
        prompt += f"{i}. {p}\n"

    for _ in range(3):  # Retry up to 3 times
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            # Split using numbered format
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
                log.write("== Prompt ==\n")
                log.write(prompt)
                log.write("\n")
                log.write("\n")
                log.write("== Response ==\n")
                log.write(content)
                log.write("\n")
                log.write("\n")
                log.write("\n")
                #raise ValueError("Mismatch between source and translated paragraph count.")
            return translations
        except Exception as e:
            print("Retrying batch due to error:", e)
            time.sleep(5)

    raise RuntimeError("Batch translation failed after 3 attempts.")

def process_fb2_to_bilingual(input_path, output_path, model, src_lang, tgt_lang, batch_size=5):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_path, parser)
    root = tree.getroot()

    nsmap = root.nsmap
    if None in nsmap:
        nsmap['fb2'] = nsmap.pop(None)

    paragraphs = root.xpath('//fb2:body//fb2:p', namespaces=nsmap)

    buffer = []
    buffer_elements = []

    for p in tqdm(paragraphs, desc="Translating paragraphs"):
        full_text = ''.join(p.itertext()).strip()
        if not full_text:
            continue
        buffer.append(full_text)
        buffer_elements.append(p)

        if len(buffer) == batch_size:
            translations = batch_translate(buffer, model, src_lang, tgt_lang)
            for orig_p, trans_text in zip(buffer_elements, translations):
                new_p = deepcopy(orig_p)
                new_p.clear()
                new_p.text = trans_text
                orig_p.addnext(new_p)
            buffer.clear()
            buffer_elements.clear()

    # Handle any remaining paragraphs
    if buffer:
        translations = batch_translate(buffer, model, src_lang, tgt_lang)
        for orig_p, trans_text in zip(buffer_elements, translations):
            new_p = deepcopy(orig_p)
            new_p.clear()
            new_p.text = trans_text
            orig_p.addnext(new_p)

    tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

def main():
    parser = argparse.ArgumentParser(description="Create bilingual FB2 files using GPT.")
    parser.add_argument("input_file", help="Path to the input FB2 file.")
    parser.add_argument("output_file", help="Path to save the bilingual FB2 output.")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model (default: gpt-4o-mini)")
    parser.add_argument("--source", default="Russian", help="Source language (default: Russian)")
    parser.add_argument("--target", default="Greek", help="Target language (default: Greek)")
    parser.add_argument("--batch", type=int, default=5, help="Batch size (default: 5)")

    args = parser.parse_args()
    process_fb2_to_bilingual(args.input_file, args.output_file, args.model, args.source, args.target, args.batch)

if __name__ == "__main__":
    main()

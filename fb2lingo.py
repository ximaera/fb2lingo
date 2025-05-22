import os
from openai import OpenAI
from lxml import etree
from copy import deepcopy
from tqdm import tqdm

client = OpenAI()

def translate_paragraph(text, source_lang="Russian", target_lang="Greek"):
    prompt = (
        f"Translate the following paragraph from {source_lang} to {target_lang}. "
        f"Preserve the structure and meaning as much as possible:\n\n{text}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def process_fb2_to_bilingual(input_path, output_path, src_lang="Russian", tgt_lang="Greek"):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_path, parser)
    root = tree.getroot()

    nsmap = root.nsmap
    if None in nsmap:
        nsmap['fb2'] = nsmap.pop(None)

    paragraphs = root.xpath('//fb2:body//fb2:p', namespaces=nsmap)

    for p in tqdm(paragraphs, desc="Translating paragraphs"):
        full_text = ''.join(p.itertext()).strip()
        if not full_text:
            continue

        translated_text = translate_paragraph(full_text, src_lang, tgt_lang)

        # Create a new paragraph node with the translated text
        translated_p = deepcopy(p)
        # Remove all children and text
        translated_p.clear()
        translated_p.text = translated_text

        # Insert translated paragraph after the original
        p.addnext(translated_p)

    # Write updated FB2 to output
    tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

if __name__ == "__main__":
    input_fb2 = "Panov_Anklavy_2_Povodyri-na-raspute.145274_short.fb2"
    output_fb2 = "bilingual_book.fb2"
    process_fb2_to_bilingual(input_fb2, output_fb2)

import argparse
import sys
import os
import io
import spacy
from spacy.matcher import Matcher
nlp = spacy.load('en_core_web_sm')

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

assets_under_mgmt_matches = []
current_page_no = 0
current_sent_no = 0

def assets_under_mgmt(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    assets_under_mgmt_matches.append((current_page_no, current_sent_no, doc[start:end].text))
    print('assets_under_mgmt match: %s' % doc[start:end].text)

matcher = Matcher(nlp.vocab)
matcher.add('AssetsUnderMgmt', None,
    [{'LEMMA': 'asset'},
       {'IS_ASCII': True, 'OP': '*'},
       {'ENT_TYPE': 'MONEY'}],
    [{'ENT_TYPE': 'MONEY'},
       {'IS_ASCII': True, 'OP': '*'},
       {'LEMMA': 'asset'}]
)

def create_arg_parser():
    """"Creates and returns the ArgumentParser object."""

    parser = argparse.ArgumentParser(description='Extracts info from fund PDFs.')
    parser.add_argument('inputPdfFile',
                    help='Path to the input PDF file to extract info from.')
    return parser

def extract_text_by_page(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)

            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
            fake_file_handle.close()

def extract_text(pdf_path):
    page_num = 1
    current_page_no = page_num
    for page in extract_text_by_page(pdf_path):
        # print(page_num)
        doc_page = nlp(page)
        sent_num = 1
        current_sent_no = sent_num
        for sent in doc_page.sents:
            # print(sent_num)
            # print(sent)
            doc_sent = nlp(sent.text)
            matches = matcher(doc_sent)
            for match_id, start, end in matches:
                assets_under_mgmt_matches.append(
                    (current_page_no,
                        current_sent_no,
                        doc_sent[start:end].text,
                        doc_sent)
                )
            sent_num += 1
            current_sent_no = sent_num
        # print()
        page_num += 1
        current_page_no = page_num

def test_matchers():
    matcher = Matcher(nlp.vocab)
    matcher.add('AssetsUnderMgmt', assets_under_mgmt,
        [{'LEMMA': 'asset'},
           {'IS_ASCII': True, 'OP': '*'},
           {'ENT_TYPE': 'MONEY'}]
    )
    doc = nlp(u'Form ADV Part 2A Item 1	– Cover Page 204 Spring	Street	Marion,	MA	02738 (508) 748‐0800 www.baldwinbrothersinc.com	March 2018 As of December 31, 2017, Baldwin Brothers’ assets under management were $1,004,785,452; $975,816,912 is managed on a discretionary basis; and $28,968,540 is managed on a non‐discretionary basis.')
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
    matcher(doc)

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    if os.path.exists(parsed_args.inputPdfFile):
        extract_text(parsed_args.inputPdfFile)
    print('Assets Under Management: ')
    print(assets_under_mgmt_matches)

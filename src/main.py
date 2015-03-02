#import PyOrgMode

from PyOrgMode import OrgDrawer, OrgNode, OrgElement, OrgDataStructure

import argparse
import shutil

import uuid

import csv

import os, os.path, re

VERBOSE = False


# logical card data and operations on org cards
class Card:
    def __init__(self, orgcard):
        self.orgcard = orgcard

    def parents_and_self(self):
        return list(self.parents()) + [self.orgcard]
        
    def parents(self):
        def all_nodes_up(e):
            while e is not None:
                yield e
                e = e.parent

        parents = list(all_nodes_up(self.orgcard))[1:-1]
        return reversed(parents)
        
    def topics(self):
        return [p.heading.strip() for p in self.parents()]

    def name(self):
        return self.orgcard.heading.strip()

    def content(self):
        return ''.join([str(e) for e in self.orgcard.content if type(e) is str])

    def tags(self):
        return self.orgcard.tags
    
    def __get_property_drawers(self):
        for e in self.orgcard.content:
            if isinstance(e, OrgDrawer.Element) and e.name == 'PROPERTIES':
                yield e

    def __get_first_property_drawer(self, add=False):
        for e in self.__get_property_drawers():
            return e

        # non found
        if add:
            pr = OrgDrawer.Element('PROPERTIES')
            self.orgcard.content = [pr] + self.orgcard.content
            pr.parent = self

            return pr

        return None
    
    def __get_named_property(self, name, add=False):
        for d in self.__get_property_drawers():
            for e in d.content:
                if isinstance(e, OrgDrawer.Property) and e.name == name:
                    return e

        if add:
            d = self.__get_first_property_drawer(add=True)
            
            id = OrgDrawer.Property('ID', '')
            id.parent = d
            d.content = [id] + d.content
            
            return id
        
        return None

    def id(self):
        c = self.__get_named_property('ID')

        return c.value if c is not None else None

    def set_id(self, id):
        c = self.__get_named_property('ID', add=True)
        c.value = id


    




# which cards to be choosen and how to format?        
    
def select_card(card):
    if not  'flashcard' in card.tags():
        return False

    for p in card.parents_and_self():
        if hasattr(p, 'todo'):
            if p.todo == 'DONE':
                return False
    
    return True

def format_card(card):
    return (card.id(), ' -- '.join(card.topics()), card.name(), str(card.content()))








        
def parse_org_file(filename):
    org = OrgDataStructure()
    org.load_from_file(filename)
    # print(org.root.output())

    return org
        
def gather_flashcards(org):
    def process(e):
        if isinstance(e, OrgNode.Element):
            c = Card(e)
            if select_card(c):
                yield c

        if isinstance(e, OrgElement):
            for c in e.content:
                for fc in process(c):
                    yield fc

    return list(process(org.root))

def append_ids(cards):
    changed = False

    for c in cards:
        if c.id() is None:
            c.set_id(str(uuid.uuid1()))
            changed = True
            
    return changed

def read_org_file_flashcards(org_file):
    org = parse_org_file(org_file)
    
    flashcards = gather_flashcards(org)
    # print(flashcards)

#    print(org.root.output())
    changed = append_ids(flashcards)
#    print(org.root.output())

    if changed:
        # create backup
        shutil.copy2(org_file, org_file+"~")

        org.save_to_file(org_file)

    return flashcards

def read_org_file_or_directory_flashcards(org_files_or_directories):
    if type(org_files_or_directories) is list:
        return [c for i in org_files_or_directories\
                for c in read_org_file_or_directory_flashcards(i)]
    
    elif os.path.isdir(org_files_or_directories):
        results = []
        
        for subdir, dirs, files in os.walk(org_files_or_directories):
            for f in files:
                if re.match('.*\.org$', f):
                    results += read_org_file_flashcards(os.path.join(org_files_or_directories, subdir, f))
        return results
    
    elif os.path.isfile(org_files_or_directories):
        return read_org_file_flashcards(org_files_or_directories)
        
def format_latex(string):
    string = re.sub('(?<!\[)\$\$(?!\])(.*)(?<!\[)\$\$(?!\])', '[$$]\\1[/$$]', string)
    string = re.sub('(?<!\[)\$(?!\])(.*)(?<!\[)\$(?!\])', '[$]\\1[/$]', string)

    # print(string)
    
    return string

def format_cards(cards):
    data = []

    for c in cards:
        data.append(tuple([format_latex(str(c)) for c in format_card(c)]))

    print(repr(data))
    
    return data

def write_csv_flashcards(csvfile, cards):
    data = format_cards(cards)
    
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    # writer.writeheader()

    for c in data:
        writer.writerow(c)

def main():
    parser = argparse.ArgumentParser(description='Extract flashcards from org-files')
    parser.add_argument('--verbose', type=bool, default=True, help='verbose output')
    parser.add_argument('--csv_file', type=str, default='flashcards.csv', help='output file') 
    parser.add_argument('org_files_or_directories', action='append', type=str, help='input file')
    args = parser.parse_args()

    VERBOSE = args.verbose

    flashcards = read_org_file_or_directory_flashcards(args.org_files_or_directories)
    
    with open(args.csv_file, 'w') as f:
        write_csv_flashcards(f, flashcards)

        

        




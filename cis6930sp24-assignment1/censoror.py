import argparse
import glob
import os
import re
import sys
from google.cloud import language_v2

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'still-smithy-358409-a22b404e9126.json'




class Censor:
    def __init__(self, output_dir, stats_file):
        self.output_dir = output_dir
        self.stats_file = stats_file
        self.stats = {'files_processed': 0, 'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0}

    def censor_content(self, content, censor_flags):
        if censor_flags['dates']:
            content,date_counter = self._censor_dates(content)
        if censor_flags['phones']:
            content, phone_counter = self._censor_phones(content)
        if censor_flags['names']:
            content, name_counter = self._censor_names(content)
        if censor_flags['addresses']:
            content, address_counter = self._censor_addresses(content)
        return content,[date_counter, phone_counter, address_counter, name_counter]

    def _censor_dates(self, content):
        counter = 0
        # Regex patterns for different date formats
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY or DD-MM-YYYY
            r'\b\d{4}/\d{1,2}/\d{1,2}\b',  # YYYY/MM/DD
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-
            r"""\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s
                       (March|April|May|June|July|August|September|October|November|December|January|February)\s
                       \d{1,2},\s\d{4}\s\d{1,2}:\d{2}\s(?:AM|PM)\b""",
            r'\b[JFMASOND][aepuco][nbrylgptvc]\d{4}\b',
            r'[JFMASOND][aepuco][nbrylgptvc][a-z]*\d{4}',
            r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{1,2} [JFMASOND][aepuco][nbrylgptvc] \d{4}\b',  # Day, DD Month YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b',  # Month DD, YYYY
            r'\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b',  # DD Month YYYY
            r'\b\d{4}\b'  # YYYY
        ]
        
        
        combined_pattern = '|'.join(date_patterns)
        
        
        def replace_with_censor(match):
            return '*' * len(match.group())
        
        counter += len(re.findall(combined_pattern, content, flags=re.IGNORECASE))

        # Censor dates in the content
        censored_content = re.sub(combined_pattern, replace_with_censor, content, flags=re.IGNORECASE)
        
        return censored_content, counter


    def _censor_phones(self, content):
        counter = 0
        # Extended phone number pattern to match various international formats
        phone_pattern = r"""
        
        (\+?\d{1,3}[\s-]?)?
        
        (\(?\d{1,3}\)?[\s-]?)?
        # First part of the number
        \d{1,4}[\s-]?
        # Second part of the number
        \d{1,4}[\s-]?
        # Third part of the number
        \d{1,4}
        
        (\s*(ext|x)\.?\s*\d{2,5})?
        """

        def replace_with_censor(match):
            return '*' * len(match.group())
        
        matches = len(re.findall(phone_pattern, content, re.VERBOSE))
        self.stats['phones'] += matches
        counter += len(re.findall(phone_pattern, content, flags=re.VERBOSE))
        content =  re.sub(phone_pattern, replace_with_censor, content, flags=re.VERBOSE)
        return content, counter

    def get_names(self, text_content):
        """
        Analyzes Entities in a string to identify names of persons.

        Args:
        text_content: The text content to analyze

        Returns:
        A list of names identified in the text.
        """
        client = language_v2.LanguageServiceClient()

        
        document_type = language_v2.Document.Type.PLAIN_TEXT

        # Create the document with the text content
        document = language_v2.Document(
            content=text_content,
            type_=document_type
        )

        
        encoding_type = language_v2.EncodingType.UTF8

        # Perform entity analysis
        response = client.analyze_entities(request={"document": document, "encoding_type": encoding_type})

        # List to store names of persons
        person_names = []

        # Process each entity in the response
        for entity in response.entities:
            # Check if the entity type is PERSON
            if entity.type_ == language_v2.Entity.Type.PERSON:
                person_names.append(entity.name)

        return person_names
    

    def get_address(self, text_content):
        client = language_v2.LanguageServiceClient()

        document = language_v2.Document(
            content=text_content,
            type_=language_v2.Document.Type.PLAIN_TEXT
        )

        response = client.analyze_entities(request={"document": document, "encoding_type": language_v2.EncodingType.UTF8})

        # List to store addresses
        addresses = []

        # Process each entity in the response
        for entity in response.entities:
            # Check if the entity type is LOCATION, which might be used for addresses
            if entity.type_ == language_v2.Entity.Type.LOCATION:
                addresses.append(entity.name)  

        return addresses
    

    def _censor_names(self, content):

        names = self.get_names(content)
        counter = 0
        
        split_names_list = []
        for name in names:
            # Splitting by space, dot, @
          
            parts = re.split(r'[ .@]+', name)
            split_names_list.extend(parts)
        names += split_names_list
       
        escaped_names = [re.escape(name) for name in names]


        # Define a list of regex patterns to match names in various contexts
        regex_patterns = []

        
        regex_patterns += [r'\b' + name + r'\b' for name in escaped_names]

        # Match names preceded or followed by certain characters like underscores, slashes, or hyphens
       
        special_chars = ['_', '-', '/']
        for char in special_chars:
            regex_patterns += [char + name for name in escaped_names]
            regex_patterns += [name + char for name in escaped_names]

        # Combine all patterns into a single pattern using alternation
        combined_pattern = '|'.join(regex_patterns)

        # Function to replace each match with the appropriate number of asterisks
        def replace_with_asterisks(match):
            return '*' * len(match.group())

        # Apply the combined pattern to censor names in the content
        counter += len(re.findall(combined_pattern, content, flags=re.IGNORECASE))
        

        censored_text = re.sub(combined_pattern, replace_with_asterisks, content, flags=re.IGNORECASE)
        email_pattern = r'(?:[a-zA-Z0-9_.+-]+)?@([a-zA-Z0-9-]+\.)+[a-zA-Z0-9-]{2,}'
        censored_text = re.sub(email_pattern, replace_with_asterisks , censored_text)
        
        return censored_text, counter

    def _censor_addresses(self, content):
        counter = 0
        # Get a list of addresses from the text content
        addresses = self.get_address(content)

        def replace_with_asterisks(match):
            return '*' * len(match.group())

        for address in addresses:
            # Escape special characters in address string for regex use
            escaped_address = re.escape(address)
            # Create a pattern for each address
            address_pattern = rf'\b{escaped_address}\b'
            
            
            # Find and replace the address in the content
            counter += len(re.findall(address_pattern, content))
            content = re.sub(address_pattern, replace_with_asterisks, content)


        zipcode_pattern = r"""
           
            (?:[A-Za-z]{2}\s)?
            # Primary 5-digit zipcode
            \d{5}
           
            (?:-\d{4})?
            |
            # International format, numeric (e.g., "400101")
            \b\d{6}\b
            |
            # International alphanumeric format (e.g., "K1A 0B1"), common in Canada, UK, etc.
            (?:[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d)
            """
        counter += len(re.findall(zipcode_pattern, content, flags=re.VERBOSE))
        content = re.sub(zipcode_pattern,replace_with_asterisks , content, flags=re.VERBOSE)
        return content, counter


    def write_stats(self):
        if self.stats_file == 'stderr':
            sys.stderr.write(str(self.stats) + '\n')
        elif self.stats_file == 'stdout':
            sys.stdout.write(str(self.stats) + '\n')
        else:
            with open(self.stats_file, 'w') as f:
                f.write(str(self.stats) + '\n')

def main():
    parser = argparse.ArgumentParser(description='Censor sensitive information from text files.')
    parser.add_argument('--input', action='append', help='Glob pattern for input files.')
    parser.add_argument('--names', action='store_true', help='Flag to censor names.')
    parser.add_argument('--dates', action='store_true', help='Flag to censor dates.')
    parser.add_argument('--phones', action='store_true', help='Flag to censor phone numbers.')
    parser.add_argument('--address', action='store_true', help='Flag to censor addresses.')
    parser.add_argument('--output', required=True, help='Directory to store all the censored files.')
    parser.add_argument('--stats', required=True, help='File or location to write the statistics of the censored files.')

    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    censor = Censor(args.output, args.stats)
    censor_flags = {'names': args.names, 'dates': args.dates, 'phones': args.phones, 'addresses': args.address}

    for pattern in args.input:
        for file_path in glob.glob(pattern):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            censored_content, censor_counts = censor.censor_content(content, censor_flags)

            base_name = os.path.basename(file_path)
            output_path = os.path.join(args.output, f"{base_name}.censored")
            with open(output_path, 'w', encoding='utf-8') as censored_file:
                censored_file.write(censored_content)

            censor.stats['files_processed'] += 1
            censor.stats["dates"] += censor_counts[0]
            censor.stats["names"] += censor_counts[3]
            censor.stats["phones"] += censor_counts[1]
            censor.stats["addresses"] += censor_counts[2]


    censor.write_stats()

if __name__ == "__main__":
    main()